import { ChartNoAxesCombined, Database } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../ui/PageHeader'
import PageFooter from '../ui/PageFooter'

function Homepage() {
    const navigate = useNavigate()
    return (
        <div className="min-h-screen font-sans text-white">
            <PageHeader />

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
                    <button
                        className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-[#1e3c72] shadow-md transition hover:scale-105 hover:bg-gray-100"
                        onClick={() => navigate('/database')}
                    >
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
                            Predicts <strong>prion-like domains (PrLDs)</strong>{' '}
                            across the human proteome using curated sequence and
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

            <section className="bg-[#f8f9fb] px-10 py-16 text-[#1e3c72] md:px-32">
                <div className="mx-auto max-w-5xl">
                    <h2 className="mb-6 w-fit border-b-2 border-blue-200 pb-2 text-3xl font-bold">
                        Methodology
                    </h2>
                    <ul className="list-disc space-y-4 pl-6 leading-relaxed text-gray-800">
                        <li>
                            <strong>Dataset Collection:</strong> Retrieved all
                            reviewed human proteins (~20,420) from UniProtKB.
                            Only canonical isoforms were retained to avoid
                            redundancy.
                        </li>
                        <li>
                            <strong>PrLD Prediction:</strong> Each sequence was
                            analyzed using <em>PLAAC</em> to detect prion-like
                            domains based on Q/N-richness and compositional
                            bias. Only proteins with a valid proline-rich domain
                            (PRD) were retained, resulting in 195 candidates.
                        </li>
                        <li>
                            <strong>Structure Retrieval & Filtering:</strong>{' '}
                            AlphaFold-predicted structures were downloaded for
                            these 195 proteins. Only 188 proteins had complete
                            structural coverage for the 195 shortlisted proteins.
                        </li>
                        <li>
                            <strong>Structural Feature Extraction:</strong>{' '}
                            Calculated solvent-accessible surface area (
                            <em>SASA</em>) and averaged AlphaFold per-residue
                            confidence scores (<em>pLDDT</em>) to assess solvent
                            exposure and intrinsic disorder within the PrLD
                            regions.
                        </li>
                        <li>
                            <strong>3D Clustering of PrLDs:</strong> Sidechain
                            centroids of residues within PrLDs were computed
                            from 3D coordinates. Clustering was performed using{' '}
                            <em>DBSCAN</em> to identify spatially cohesive
                            substructures. All clusters were visualized using
                            PyMOL and NGL Viewer.
                        </li>
                    </ul>
                </div>
            </section>

            <PageFooter />
        </div>
    )
}

export default Homepage
