export function PrdInfoPanel({ data }) {
    if (!data) return null

    return (
        <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 text-[#1e3c72] shadow-sm">
            <h2 className="mb-4 text-xl font-semibold tracking-wide text-[#1e3c72]">
                Proline Rich Domain (PRD)
            </h2>
            <div className="my-4 rounded-lg bg-blue-50 p-4 text-sm text-[#1e3c72] shadow-sm">
                <h3 className="mb-2 text-base font-semibold">
                    What is a Proline-Rich Domain?
                </h3>
                <p>
                    Proline-rich domains (PRDs) are segments of proteins with a
                    high content of proline residues. These domains play crucial
                    roles in protein-protein interactions and often overlap with
                    prion-like regions. PRDs can affect the aggregation behavior
                    of proteins and are implicated in various neurodegenerative
                    diseases.
                </p>
            </div>

            <div className="grid grid-cols-1 gap-4 px-10 text-sm text-[#1e3c72] md:grid-cols-3">
                <div className="rounded-lg border border-blue-200 bg-white p-3 text-center shadow-sm">
                    <div className="font-semibold text-blue-800">
                        PRD Start Position
                    </div>
                    <div className="mt-1 font-mono text-lg">
                        {data.PRDstart}
                    </div>
                </div>
                <div className="rounded-lg border border-blue-200 bg-white p-3 text-center shadow-sm">
                    <div className="font-semibold text-blue-800">
                        PRD End Position
                    </div>
                    <div className="mt-1 font-mono text-lg">{data.PRDend}</div>
                </div>
                <div className="rounded-lg border border-blue-200 bg-white p-3 text-center shadow-sm">
                    <div className="font-semibold text-blue-800">Length</div>
                    <div className="mt-1 font-mono text-lg">
                        {data.PRDlen} aa
                    </div>
                </div>
                <div className="rounded-lg border border-blue-200 bg-white p-3 text-center shadow-sm">
                    <div className="font-semibold text-blue-800">SASA<span className="text-red-600">*</span></div>
                    <div className="mt-1 font-mono text-lg">
                        {parseFloat(data.SASA).toFixed(2)} Å²
                    </div>
                </div>
                <div className="rounded-lg border border-blue-200 bg-white p-3 text-center shadow-sm">
                    <div className="font-semibold text-blue-800">
                        Avg pLDDT<span className="text-red-600">*</span>
                    </div>
                    <div className="mt-1 font-mono text-lg">
                        {parseFloat(data.Average_pLDDT).toFixed(2)}
                    </div>
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
