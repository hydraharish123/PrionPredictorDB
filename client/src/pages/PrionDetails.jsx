import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { ProteinMetadataCard } from '../features/details-page/ProteinMetadataCard'
import { PrdInfoPanel } from '../features/details-page/PrdInfoPanel'
import { NglViewer } from '../features/details-page/NGLviewer'
import PageFooter from '../ui/PageFooter'
import AggreScan3dChart from '../features/details-page/AggreScan3dChart'

function PrionDetails() {
    const { id } = useParams()
    const [fileData, setFileData] = useState(null)
    const [proteinData, setProteinData] = useState(null)

    useEffect(() => {
        if (!id) return
        const fetchDetails = async () => {
            try {
                const res = await fetch(
                    `http://localhost:3000/api/v1/prion-proteins/${id}`
                )
                const data = await res.json()
                setFileData(data?.data?.files?.[0])
                setProteinData(data?.data?.data?.[0])
            } catch (err) {
                console.error(err)
            }
        }
        fetchDetails()
    }, [id])

    return (
        <div className="min-h-screen font-sans text-white">
            <header className="flex w-full items-center justify-between border-b border-white/20 bg-[rgb(0,99,154)] px-8 py-4 text-white backdrop-blur-sm">
                <h1 className="text-2xl font-bold tracking-wide">
                    PrionPredictorDB
                </h1>

                <div className="flex items-center gap-4 text-sm">
                    <h2 className="cursor-pointer font-semibold">
                        Documentation
                    </h2>
                    <h2 className="cursor-pointer font-semibold">Contact</h2>
                    <span className="opacity-80">Release v1.0</span>
                </div>
            </header>

            <main className="flex flex-col gap-6 px-6 py-12 md:px-20">
                <h2 className="text-2xl font-semibold text-[#1e3c72] shadow-sm">
                    Prion - {id}
                </h2>

                <ProteinMetadataCard data={proteinData} />
                <PrdInfoPanel data={proteinData} />
                {fileData?.a3d_csv && (
                    <AggreScan3dChart csv_url={fileData.a3d_csv} />
                )}

                {fileData?.pdb && (
                    <NglViewer
                        data={proteinData}
                        csv_url={fileData.a3d_csv}
                        pdbUrl={fileData.pdb}
                        centroidsUrl={fileData.centroids}
                        clusteringUrl={fileData.clustering}
                    />
                )}
            </main>

            <PageFooter />
        </div>
    )
}

export default PrionDetails
