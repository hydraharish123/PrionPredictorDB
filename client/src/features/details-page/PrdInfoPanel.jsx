export function PrdInfoPanel({ data }) {
    if (!data) return null

    return (
        <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 text-[#1e3c72] shadow-sm">
            <h2 className="mb-4 text-xl font-semibold tracking-wide text-[#1e3c72]">
                📊 PRD Info
            </h2>
            <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
                <div>
                    <span className="font-medium">PRD Start:</span>{' '}
                    {data.PRDstart}
                </div>
                <div>
                    <span className="font-medium">PRD End:</span> {data.PRDend}
                </div>
                <div>
                    <span className="font-medium">Length:</span> {data.PRDlen}{' '}
                    aa
                </div>
                <div>
                    <span className="font-medium">SASA:</span>{' '}
                    {parseFloat(data.SASA).toFixed(2)} Å²
                </div>
                <div>
                    <span className="font-medium">Avg pLDDT:</span>{' '}
                    {parseFloat(data.Average_pLDDT).toFixed(2)}
                </div>
            </div>

            <div className="mt-5">
                <span className="font-medium">PRD Sequence:</span>
                <div className="mt-2 max-h-[100px] overflow-auto rounded-md bg-gray-100 p-3 font-mono text-xs text-blue-900">
                    {data.PRDaa}
                </div>
            </div>
        </div>
    )
}
