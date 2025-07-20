# -*- coding: utf-8 -*-

"""Module to handle pdb files."""

import os
import logger
import re
import gzip
from urllib2 import urlopen, HTTPError, URLError
from StringIO import StringIO
import json

_name = "PDB"

class Pdb:
    """
    Pdb parser. Initialized by:
    1. pdb filename
    2. gzipped pdb filename
    3. 4-letter pdb code
    """

    def __init__(self,*args, **kwargs):
        self.file_name = None
        self.pdb_code = None
        self.dir = os.getcwd()
        self.loc = os.path.join(self.dir, "input_pdb")
        self.codification = {"ALA" : 'A', "CYS" : 'C', "ASP" : 'D', "GLU" : 'E', "PHE" : 'F', "GLY" : 'G', "HIS" : 'H',
                             "ILE" : 'I', "LYS" : 'K', "LEU" : 'L', "MET" : 'M', "MSE" : 'M', "ASN" : 'N', "PYL" : 'O',
                             "PRO" : 'P', "GLN" : 'Q', "ARG" : 'R', "SER" : 'S', "THR" : 'T', "SEC" : 'U', "VAL" : 'V',
                             "TRP" : 'W', "5HP" : 'E', "ABA" : 'A', "AIB" : 'A', "BMT" : 'T', "CEA" : 'C', "CGU" : 'E',
                             "CME" : 'C', "CRO" : 'X', "CSD" : 'C', "CSO" : 'C', "CSS" : 'C', "CSW" : 'C', "CSX" : 'C',
                             "CXM" : 'M', "DAL" : 'A', "DAR" : 'R', "DCY" : 'C', "DGL" : 'E', "DGN" : 'Q', "DHI" : 'H',
                             "DIL" : 'I', "DIV" : 'V', "DLE" : 'L', "DLY" : 'K', "DPN" : 'F', "DPR" : 'P', "DSG" : 'N',
                             "DSN" : 'S', "DSP" : 'D', "DTH" : 'T', "DTR" : 'X', "DTY" : 'Y', "DVA" : 'V', "FME" : 'M',
                             "HYP" : 'P', "KCX" : 'K', "LLP" : 'K', "MLE" : 'L', "MVA" : 'V', "NLE" : 'L', "OCS" : 'C',
                             "ORN" : 'A', "PCA" : 'E', "PTR" : 'Y', "SAR" : 'G', "SEP" : 'S', "STY" : 'Y', "TPO" : 'T',
                             "TPQ" : 'F', "TYS" : 'Y', "TYR" : 'Y' }
        keys = self.codification.keys()
        self.sequences = {}
        self.onlycalfa = ""
        self.allatoms = ""
        self.chain = ""
        self.canumber = 0
        self.allnumber = 0

        if args and len(args) == 1:
            if args[0] is None: raise logger.AggrescanError("No pdb code/file provided. Quitting.",
                                                            module_name=_name)
            if os.path.isfile(args[0]):
                self.file_name = args[0]
            else:
                self.pdb_code = args[0]
        if kwargs:
            self.loc = kwargs['output']
            try:
                self.chain = kwargs['chain']
            except KeyError:
                pass

        if self.file_name:
            try:
                self.handler = gzip.GzipFile(filename=self.file_name)
                self.data = self.handler.readlines()
                logger.debug(module_name=_name, msg="Reading %s" % os.path.abspath(self.file_name))
            except IOError:
                try:
                    self.handler = open(self.file_name)
                    self.data = self.handler.readlines()
                    logger.debug(module_name=_name, msg="Reading %s" % os.path.abspath(self.file_name))
                except IOError:
                    raise logger.AggrescanError("Couldnt open specified filename %s. Quitting.' % os.path.abspath(self.file_name)",
                                                module_name=_name)
        elif self.pdb_code:
            self.handler = self.download_pdb()
            self.data = self.handler.readlines()

        seq = re.compile(r"^ATOM.{9}CA..(?P<seqid>.{3}).(?P<chain>.{1})(?P<resid>.{4})")  # TODO zle dla alternatywnych
        if self.chain != '':
            atm = re.compile(r"^ATOM.{9}(.{2}).( |A).{4}" + self.chain + "(?P<resid>.{4})(?P<x>.{12})(?P<y>.{8})(?P<z>.{8})")
        else:
            atm = re.compile(r"^ATOM.{9}(.{2}).( |A).{5}(?P<resid>.{4})(?P<x>.{12})(?P<y>.{8})(?P<z>.{8})")

        ter = re.compile(r'^END|^TER')
        mod = re.compile(r"^ENDMDL")
        self.trajectory = []
        self.sequence = ""

        lines = self.data
        end = len(lines) - 1
        counter = 0
        self._chainsOrder(lines)
        self._resIndexes(lines)
        self.mutatedata = {}

        for line in lines:
            line = re.sub(r'^HETATM(.{11})MSE(.*$)', r'ATOM  \1MET\2', line)
            localData = atm.match(line)
            data_seq = seq.match(line)

            if data_seq:
                seqid = data_seq.groups()[0].strip()
                chainid = data_seq.groups()[1].strip()
                resid = data_seq.groups()[2].strip()

                if seqid in keys:
                    s = self.codification[seqid]
                else:
                    s = "X"
                self.sequence += s

                # add to mutate page
                if chainid in self.mutatedata.keys():
                    self.mutatedata[chainid].append({'chain': chainid,
                                                     'resname': s,
                                                     'residx': resid})
                else:
                    self.mutatedata[chainid] = [{'chain': chainid,
                                                 'resname': s,
                                                 'residx': resid}]

                if chainid in self.sequences.keys():
                    self.sequences[chainid] += s
                else:
                    self.sequences[chainid] = s

            if localData:
                self.allnumber += 1
                self.allatoms += line
                dg = localData.groups()
                if dg[0] == 'CA':
                    self.onlycalfa += line
                    self.canumber += 1

            if counter == end:
                self.onlycalfa += line
                self.allatoms += line
            if ter.match(line):
                if self.chain:
                    if line[21] == self.chain:
                        self.onlycalfa += line
                        self.allatoms += line
                else:
                    self.onlycalfa += line
                    self.allatoms += line

            if (mod.match(line) and len(self.onlycalfa) > 1) or counter == end:
                break
            counter += 1
        self.handler.close()

    def _resIndexes(self, body):
        atm = re.compile(r"^ATOM.{9}CA..(?P<seqid>.{3}).(?P<chain>.{1})(?P<resid>.{4})")
        ter = re.compile(r'^END|^TER')
        mod = re.compile(r"^ENDMDL")
        self.numb = {}
        for chain in self.chains_order:
            self.numb[chain] = []

        for line in body:
            d = atm.match(line)
            if d:
                self.numb[d.group('chain').strip()].append(int(d.group('resid')))
            if mod.match(line):
                break

    def _chainsOrder(self, body):
        atm = re.compile(r"^ATOM.{9}CA..(?P<seqid>.{3}).(?P<chain>.{1})(?P<resid>.{4})")
        self.chains_order = []
        for line in body:
            d = atm.match(line)
            if d and d.group('chain') not in self.chains_order:
                self.chains_order.append(d.group('chain'))

    def isSingleChain(self):
        if self.chain != '' or len(self.sequences.keys()) == 1:
            return True
        else:
            return False

    def containsOnlyCA(self):
        if self.allnumber == self.canumber:
            return True
        else:
            return False

    def isBroken(self):
        brk = []
        if self.chain != '':
            indexes = self.numb[self.chain]
            first = indexes[0]
            for i in range(1, len(indexes)):
                if indexes[i] - 1 != first:
                    brk.append(str(first) + "-" + str(indexes[i]))
                first = indexes[i]
        else:
            for chain in self.sequences.keys():
                indexes = self.numb[chain]
                first = indexes[0]
                for i in range(1, len(indexes)):
                    if indexes[i] - 1 != first:
                        brk.append(str(first) + "-" + str(indexes[i]))
                    first = indexes[i]
        if len(brk) > 0:
            return ", ".join(brk)
        return False

    def getResIndexes(self):
        t = [str(i) for i in self.numb[self.chain]]
        return ",".join(t)

    def getBody(self):
        return self.allatoms

    def containsChain(self, chain):
        if chain in self.sequences.keys():
            return True

    def getSequenceNoHTML(self):
        if self.chain != '':
            return self.sequences[self.chain]
        else:
            out = ""
            for k in self.sequences.keys():
                out += "".join(self.sequences[k])
            return out

    def getSequence(self):
        if self.chain != '':
            return "<strong>" + self.chain + "</strong>: " + self.sequences[self.chain]
        else:
            out = ""
            for k in self.sequences.keys():
                out += "<strong>" + k + "</strong>: "
                out += "".join(self.sequences[k])
                out += "<br>"
            return out

    def getChainIdxResname(self):
        if self.chain == '':
            return json.dumps(self.mutatedata)
        else:
            return json.dumps({self.chain: self.mutatedata[self.chain]})

    def savePdbFile(self,path=''):
        if path:
            logger.to_file(filename=path, content=self.allatoms, allow_err=True)
        else:
            logger.to_file(filename=self.loc, content=self.allatoms, allow_err=True)

    def getPath(self):
        if os.path.isfile(self.loc):
            return self.loc
        else:
            raise logger.AggrescanError("Location for pdb file requested at: %s. The file was not found." % self.loc,
                                        module_name=_name)

    def download_pdb(self):
        try:
            gz_string = urlopen('http://www.rcsb.org/pdb/files/' + self.pdb_code.lower() + '.pdb.gz').read()
        except HTTPError as e:
            raise logger.AggrescanError("Could not download the pdb file. %s is not a valid pdb code/file. " % self.pdb_code,
                                        module_name=_name)

        except URLError as e:
            raise logger.AggrescanError("Could not download the pdb file. Can't connect to the PDB database - quitting",
                                        module_name=_name)
        fileLike = StringIO(gz_string)
        logger.debug(module_name=_name, msg="Successfully downloaded %s" % self.pdb_code.lower() + '.pdb.gz')
        return gzip.GzipFile(fileobj=fileLike,mode="rb")

    def validate(self):
        logger.debug(module_name=_name,msg='Validating pdb file: %s' % self.loc)
        if self.chain != '' and not self.containsChain(self.chain):
            raise logger.AggrescanError("Selected chain: %s not found in the pdb file. Quitting." % self.chain,
                                        module_name=_name)
        seq = self.getSequence()
        seq = re.sub("<strong>\w+</strong>:", "", seq)
        seq = re.sub("<br>", "", seq)
        seq = seq.replace(" ", "")
        allowed_seq = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L',
                       'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                       'W', 'Y']
        if len(seq) < 4:
            raise logger.AggrescanError("Sequence too short (perhaps something went wrong with pdb parsing).",
                                        module_name=_name)
        for e in seq:
            if e not in allowed_seq:
                raise logger.AggrescanError("Not supported amino acid: %s found in pdb file. Quitting." % e,
                                             module_name=_name)



if __name__ == '__main__':
    pass
