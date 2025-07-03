import { ChartNoAxesCombined, Database } from 'lucide-react'
function App() {
    return (
        <div className="min-h-screen font-sans text-white">
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

            <main className="flex flex-col items-center justify-center bg-gradient-to-br from-[#1e3c72] to-[#4b80dd] px-6 py-24 text-center text-white md:py-32">
                <h2 className="mb-6 text-4xl font-extrabold tracking-tight drop-shadow-xl md:text-5xl">
                    Predict & Explore Prion-like Proteins
                </h2>
                <p className="max-w-2xl text-lg leading-relaxed text-white/90">
                    <strong>PrionPredictorDB</strong> is your gateway to
                    prion-like domain prediction, aggregation propensity data,
                    and structure-function annotations of human proteins.
                </p>

                <div className="mt-8 flex flex-wrap gap-4">
                    <button className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-[#1e3c72] shadow-md transition hover:scale-105 hover:bg-gray-100">
                        View Database
                    </button>
                    <button className="rounded-lg bg-[#f1f5ff] px-6 py-3 text-sm font-semibold text-[#1e3c72] shadow-md transition hover:scale-105 hover:bg-white">
                        Predict
                    </button>
                </div>
            </main>

            <section className="grid grid-cols-1 gap-12 bg-white px-10 py-16 text-[#1e3c72] md:grid-cols-2 md:px-32">
                <div className="flex flex-col justify-center">
                    <h2 className="mb-4 inline-flex w-fit items-center gap-2 border-b border-blue-300 pb-2 text-2xl font-bold">
                        <ChartNoAxesCombined />
                        About Prions
                    </h2>
                    <ul className="text-md list-none space-y-4 leading-relaxed text-gray-800">
                        <li>
                            <strong>Prions</strong> are misfolded proteins
                            capable of inducing abnormal folding in other
                            proteins, often leading to neurodegenerative
                            diseases.
                        </li>
                        <li>
                            In humans, prion-related disorders include{' '}
                            <em>Creutzfeldt–Jakob disease (CJD)</em>,{' '}
                            <em>Fatal Familial Insomnia</em>, and <em>Kuru</em>.
                        </li>
                        <li>
                            Beyond classical prion diseases, proteins with{' '}
                            <strong>prion-like domains (PrLDs)</strong> are
                            found across the human proteome and are implicated
                            in conditions like ALS and Alzheimer's.
                        </li>
                    </ul>
                </div>

                <div className="flex flex-col justify-center">
                    <h2 className="mb-4 inline-flex w-fit items-center gap-2 border-b border-blue-300 pb-2 text-2xl font-bold">
                        <Database />
                        Why use PrionPredictorDB?
                    </h2>
                    <ul className="text-md list-none space-y-4 leading-relaxed text-gray-800">
                        <li>
                            Predicts{' '}
                            <strong>prion-like domains (PrLDs)</strong> across
                            the human proteome using curated sequence and
                            structure-based features.
                        </li>
                        <li>
                            Integrates{' '}
                            <strong>
                                aggregation risk, structural disorder (pLDDT)
                            </strong>
                            , and <strong>surface exposure (SASA)</strong> to
                            prioritize biologically relevant regions.
                        </li>
                        <li>
                            Offers an interactive, searchable database of
                            annotated human proteins with links to function,
                            structure.
                        </li>
                    </ul>
                </div>
            </section>

            <section>
                
            </section>
        </div>
    )
}

export default App
