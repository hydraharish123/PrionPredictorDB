import { ChartNoAxesCombined } from 'lucide-react'
import { useState, useMemo } from 'react'
import { protein_data } from '../data/test_protein_data'
import PPDB from '../data/PPDB.json'

const rawProteinData = PPDB

const uniqueProteinData = Array.from(
    new Map(rawProteinData.map((p) => [p.uniprot_id, p])).values()
)

export default function Database() {
    const [search, setSearch] = useState('')

    const filteredData = useMemo(() => {
        return uniqueProteinData.filter((p) =>
            `${p.uniprot_id} ${p.EntryName} ${p.ProteinName}`
                .toLowerCase()
                .includes(search.toLowerCase())
        )
    }, [search])

    const totalProteins = uniqueProteinData.length
    const AggregatingCount = uniqueProteinData.filter((p) => p['Aggregating-like'] === 'Yes').length

    return (
        <div className="min-h-screen font-sans text-white">
            <header className="flex w-full items-center justify-between border-b border-white/20 bg-[rgb(0,99,154)] px-8 py-4 text-white backdrop-blur-sm">
                <h1 className="text-2xl font-bold tracking-wide">
                    PrionPredictorDB
                </h1>
                <input
                    type="text"
                    placeholder="Search proteins by ID or name..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full border px-4 py-2 text-sm text-black shadow md:max-w-96"
                />
                <div className="flex items-center gap-4 text-sm">
                    <h2 className="cursor-pointer font-semibold">
                        Documentation
                    </h2>
                    <h2 className="cursor-pointer font-semibold">Contact</h2>
                    <span className="opacity-80">Release v1.0</span>
                </div>
            </header>

            <main className="px-6 py-12 md:px-20">
                <div className="mb-4 flex flex-col gap-3 text-[#1e3c72] md:flex-row md:items-center md:justify-between">
                    <h2 className="w-fit text-2xl font-bold">Prion Database</h2>
                    <div className="flex items-center gap-3 text-sm">
                        <span>
                            Showing {filteredData.length} / {totalProteins}{' '}
                            proteins
                        </span>
                        <span className="text-green-600">
                            ({AggregatingCount} Aggregating-like)
                        </span>
                    </div>
                </div>

                <div className="overflow-x-auto rounded-xl bg-white shadow-md">
                    <table className="min-w-full table-auto text-left text-sm text-[#1e3c72]">
                        <thead className="bg-[rgb(0,99,154)] text-white">
                            <tr>
                                <th className="px-4 py-3">UniProt ID</th>
                                <th className="px-4 py-3">Entry Name</th>
                                <th className="px-4 py-3">Protein Name</th>
                                <th className="px-4 py-3">Organism</th>
                                <th className="px-4 py-3 text-center">
                                    Length
                                </th>
                                <th className="px-4 py-3">Aggregating-like</th>

                                <th className="px-4 py-3">Gene Names</th>
                                <th className="px-4 py-3">Function</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-blue-100">
                            {filteredData.map((protein, idx) => (
                                <tr
                                    key={protein.uniprot_id + idx}
                                    className="odd:bg-white even:bg-blue-50/40 hover:bg-blue-50"
                                >
                                    <td className="px-4 py-2 font-mono text-blue-700 underline">
                                        <a
                                            href={`https://www.uniprot.org/uniprotkb/${protein.uniprot_id}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            {protein.uniprot_id}
                                        </a>
                                    </td>
                                    <td className="px-4 py-2">
                                        {protein['Entry Name']}
                                    </td>
                                    <td className="px-4 py-2">
                                        {protein['Protein Name']}
                                    </td>
                                    <td className="px-4 py-2">
                                        {protein.Organism}
                                    </td>
                                    <td className="px-4 py-2 text-center">
                                        {protein.Length}
                                    </td>
                                    <td className="px-4 py-2">
                                        <span
                                            className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
                                                protein['Aggregating-like'] === 'Yes'
                                                    ? 'bg-green-100 text-green-700'
                                                    : 'bg-red-100 text-red-700'
                                            }`}
                                        >
                                            {protein['Aggregating-like']}
                                        </span>
                                    </td>

                                    <td className="px-4 py-2">
                                        {protein['Gene Names']}
                                    </td>
                                    <td
                                        className="max-w-xs truncate px-4 py-2"
                                        title={protein['Function']}
                                    >
                                        {protein['Function']}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </main>

            <footer className="bg-stone-200 py-4 text-center text-sm text-stone-600">
                © 2025 PrionPredictorDB — All rights reserved.
            </footer>
        </div>
    )
}
