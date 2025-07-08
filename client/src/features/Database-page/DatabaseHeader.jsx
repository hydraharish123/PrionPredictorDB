function DatabaseHeader({ search, setSearch }) {
    return (
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
                <h2 className="cursor-pointer font-semibold">Documentation</h2>
                <h2 className="cursor-pointer font-semibold">Contact</h2>
                <span className="opacity-80">Release v1.0</span>
            </div>
        </header>
    )
}

export default DatabaseHeader
