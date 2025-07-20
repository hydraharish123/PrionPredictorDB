# -*- coding: utf-8 -*-

import re
import urllib2
import gzip
import os
from StringIO import StringIO
from utils import query_db

from wtforms.validators import DataRequired, Length, Email, optional, \
    ValidationError, NumberRange

from parsePDB import PdbParser
# from config_manager import config

###
### Validators shared by CABS and aggrescan
###


def pdb_input_validator(form, field):
    if form.input_pdb_code.data and form.input_file.data:
        raise ValidationError('Please provide either a PDB code or file, not both.')
    if not form.input_pdb_code.data and not form.input_file.data:
        raise ValidationError('Protein PDB code or PDB file is required')
    if len(field.data) < 4 and not form.input_file.data:
        raise ValidationError('Protein code must be 4-letter (2PCY).'
                              'Leave empty only if PDB file is provided')


def sequence_validator(form, field):
    allowed_seq = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N',
                   'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']
    for letter in re.sub("\s", "", field.data):
        if letter not in allowed_seq:
            raise ValidationError('Sequence contains non-standard aminoacid \
                                  symbol: %s' % letter)


def pdb_file_validator(form, field):
    if form.input_file.data:
        p = PdbParser(form.input_file.data.stream,  form.chain.data.strip())
        _structure_pdb_validator(p)


def pdb_code_validator(form, field):
    if len(form.input_pdb_code.data.strip()) == 4:
        pdb_code = field.data.strip()
        try:
            buraki = urllib2.urlopen('http://www.rcsb.org/pdb/files/'+pdb_code+'.pdb.gz')
        except:
            raise ValidationError("Could not download your protein file from pdb server. Wrong code perhaps?")

        b2 = buraki.read()
        ft = StringIO(b2)
        buraki.close()
        with gzip.GzipFile(fileobj=ft, mode="rb") as f:
            p = PdbParser(f)
            _structure_pdb_validator(p, form.chain.data.strip())

    elif not form.input_pdb_code.data:
        pass
    else:
        raise ValidationError("PDB code should contain exactly 4 characters.")


def non_empty_file(form, field):
    """To be used with files only"""
    if field.data:
        field.data.stream.seek(0, os.SEEK_END)
        if field.data.stream.tell() < 1:
            raise ValidationError("Empty file provided.")
        field.data.stream.seek(0)


def _structure_pdb_validator(p, chains=''):
    """
    :param p: parsePDB PdbParser object
    :param chains: a list of chain (might also be an empty string)
    :return: None, raises ValidationError if any errors are found
    """
    missing = p.getMissing()
    seq = p.getSequence()
    n_chains = p.get_num_chains()
    defined_chains = set(chains)
    actual_chains = set(p.getChains())
    allowed_seq = ['A', 'C', 'D', ' ', 'E', 'F', 'G', 'H', 'I', 'K', 'L',
                   'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']
    _max_length = 2000
    _max_chains = 10
    for e in seq:
        if e not in allowed_seq:
            raise ValidationError('Non-standard residue in the input \
                    structure')
    for length in p.getChainLengths():
        if length < 4:
            raise ValidationError("One of the chains in the supplied pdb file is too short."
                                  " Minimal chain length for the simulation is 4.")
    if len(seq) == 0:
        raise ValidationError('Your pdb file doesnt seem to contain a chain. The server could not extract a sequence.')
    if len(seq) > _max_length:
        raise ValidationError('CABS-flex allows max %d receptor \
                               residues. Provided file contains \
                               %d' % (_max_length, len(seq)))
    if n_chains > _max_chains:
        raise ValidationError('CABS-flex allows a maximum of %d chains.' 
                              'Your protein has: %d' % (n_chains, _max_chains))
    if missing > 5:
        raise ValidationError('Missing atoms within protein (M+N = %d). \
                Protein must fulfill M+N<6, where M - number of \
                chains, N - number of breaks' % (missing))
    if not defined_chains.issubset(actual_chains):
        raise ValidationError("Wrong chain selection. Your PDB contains chain(s): %s and you tried to select chain(s): %s" %
                              (", ".join(actual_chains), ", ".join(defined_chains)))


def only_letters_validator(form, field):
    pattern = re.compile("[^a-zA-Z\s]")
    if pattern.findall(field.data):
        raise ValidationError("Only letters and whitespaces are allowed in the chain field. You entered: %s" % field.data)

###
### Aggrescan specific validators
###


def foldx_validator(form, field):
    """check if a valid foldx loc is stored in the database"""
    if field.data == '1':
        foldx_path = query_db("SELECT foldx_path FROM system_data WHERE id=1", one=True)[0]
        req_file = os.path.join(foldx_path, 'rotabase.txt')
        if not os.path.isfile(req_file):
            raise ValidationError("Trying to run Stability calculations without a proper FoldX path specified."
                                  " (%s missing rotabase.txt file)" % foldx_path)


def foldx_and_m_validator(form, field):
    if field.data == "1" and form.foldx.data != "1":
        raise ValidationError("Please select the Stability calculations option if you wish to create a mutant.")


def single_chain_validator(form, field):
    pattern = re.compile("[^a-zA-Z\s]")
    if pattern.findall(field.data):
        raise ValidationError("Only letters and whitespaces are allowed in the chain field. You entered: %s" % field.data)
    elif len(field.data.replace(" ", "")) > 1:
        raise ValidationError("Please select a single chain")


def auto_mut_validator(form, field):
    if field.data == "1" and form.foldx.data != "1":
        raise ValidationError("Please select the Stability calculations option if you wish to use mutation options.")
    if field.data == "1" and form.dynamic.data == "1":
        raise ValidationError("Automatic mutations do not support the dynamic module. Please select either of those")