export function ProteinMetadataCard({ data }) {
    if (!data) return null
    console.log(data)
    return (
        <div className="rounded-2xl border border-gray-200 bg-white p-6 text-[#1e3c72] shadow-sm">
            <h2 className="mb-4 text-2xl font-semibold tracking-wide text-[#1e3c72]">
                Metadata
            </h2>
            <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
                <div>
                    <span className="font-medium">Entry Name:</span>{' '}
                    {data['Entry Name'] || '-'}
                </div>
                <div>
                    <span className="font-medium">UniProt ID:</span>{' '}
                    {data.uniprot_id || '-'}
                </div>
                <div>
                    <span className="font-medium">Protein Name:</span>{' '}
                    {data['Protein Name'] || '-'}
                </div>
                <div>
                    <span className="font-medium">Gene:</span>{' '}
                    {data['Gene Names'] || '-'}
                </div>
                <div>
                    <span className="font-medium">Length:</span>{' '}
                    {data.Length ? `${data.Length} aa` : '-'}
                </div>

                <div>
                    <span className="font-medium">Aggregating-like:</span>{' '}
                    <span
                        className={`ml-2 inline-block rounded px-2 py-0.5 text-xs font-semibold ${
                            data['Aggregating-like'] === 'Yes'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                        }`}
                    >
                        {data['Aggregating-like'] || '-'}
                    </span>
                </div>
            </div>
            <div className="mt-6">
                <span className="font-medium">Function:</span>{' '}
                {data.Function || '-'}
            </div>
        </div>
    )
}
