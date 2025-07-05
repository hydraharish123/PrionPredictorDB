function PageHeader() {
    return (
        <header className="flex w-full items-center justify-between border-b border-white/20 bg-white/5 px-8 py-5 text-[#1e3c72] backdrop-blur-sm">
            <h1 className="text-2xl font-bold tracking-wide">
                PrionPredictorDB
            </h1>
            <div className="flex items-center gap-4">
                <h2 className="font-semibold">Documentation</h2>
                <h2 className="font-semibold">Contact</h2>
                <span className="text-sm font-medium opacity-80">
                    Release v1.0
                </span>
            </div>
        </header>
    )
}

export default PageHeader
