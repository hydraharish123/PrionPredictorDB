import { useState, useEffect } from 'react'
import DatabaseHeader from '../features/Database-page/DatabaseHeader'
import PageFooter from './../ui/PageFooter'
import { Link } from 'react-router-dom';

export default function Database() {
    const [search, setSearch] = useState('')
    const [prionData, setPrionData] = useState([])
    const [page, setPage] = useState(1)
    const [totalPages, setTotalPages] = useState(1)

    const fetchData = async () => {
        try {
            const res = await fetch(
                `http://127.0.0.1:3000/api/v1/prion-proteins?page=${page}`,
                {
                    method: 'GET',
                }
            )
            const out = await res.json()
            if (!res.ok) throw new Error('Could not fetch results')
            setTotalPages(out?.totalPage)
            setPrionData(out)
            console.log(out)
        } catch (err) {
            console.error(err)
        }
    }

    useEffect(
        function () {
            fetchData(page)
        },
        [page]
    )

    return (
        <div className="min-h-screen font-sans text-white">
            <DatabaseHeader search={search} setSearch={setSearch} />

            <main className="px-6 py-12 md:px-20">
                <div className="mb-4 flex flex-col gap-3 text-[#1e3c72] md:flex-row md:items-center md:justify-between">
                    <h2 className="w-fit text-2xl font-bold">Prion Database</h2>
                    <div className="flex items-center gap-3 text-sm">
                        <span>Showing {prionData?.result} proteins</span>
                        <span className="text-green-600">
                            {prionData?.aggregating} Aggregating-like
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
                            {prionData?.data?.data?.map((protein, idx) => (
                                <tr
                                    key={protein.uniprot_id + idx}
                                    className="odd:bg-white even:bg-blue-50/40 hover:bg-blue-50"
                                >
                                    <td className="px-4 py-2 font-mono text-blue-700 underline">
                                        <Link
                                            to={`/database/${protein.uniprot_id}`}
                                            className="cursor-pointer text-blue-600 hover:underline"
                                        >
                                            {protein.uniprot_id}
                                        </Link>
                                    </td>
                                    <td className="px-4 py-4">
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
                                                protein['Aggregating-like'] ===
                                                'Yes'
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
                    <div className="flex items-center justify-between border border-t-2 bg-stone-50 px-4 py-3">
                        <span className="text-gray-400">Page {page}</span>
                        <div className="space-x-2">
                            <button
                                disabled={page == 1}
                                onClick={() => setPage((page) => page - 1)}
                                className="rounded border border-stone-300 bg-white px-3 py-1 text-gray-400 disabled:opacity-40"
                            >
                                Prev
                            </button>
                            <button
                                disabled={page == totalPages}
                                onClick={() => setPage((page) => page + 1)}
                                className="rounded border border-stone-300 bg-white px-3 py-1 text-gray-400 disabled:opacity-40"
                            >
                                Next
                            </button>
                        </div>
                    </div>
                </div>
            </main>

            <PageFooter />
        </div>
    )
}
