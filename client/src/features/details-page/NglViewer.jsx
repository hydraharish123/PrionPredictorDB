import { useRef, useEffect, useState } from 'react'
import { loadNGL } from '../../utils/loadNGL'
import Papa from 'papaparse'

function generateClusterColors(n) {
    const colors = []
    const step = 360 / n
    for (let i = 0; i < n; i++) {
        const hue = Math.round(i * step)
        colors.push(`hsl(${hue}, 70%, 50%)`)
    }
    return colors
}

export function NglViewer({ pdbUrl, centroidsUrl, clusteringUrl, csv_url }) {
    const viewerRef = useRef()
    const [clusteringData, setClusteringData] = useState({})
    const [clusterColors, setClusterColors] = useState([])
    const [csvData, setCSVdata] = useState([])
    const [mapped, setMapped] = useState([])
        useEffect(() => {
            fetch(`http://localhost:3000${csv_url}`)
                .then((response) => response.text())
                .then((csvText) => {
                    const parsed = Papa.parse(csvText, {
                        header: true,
                        skipEmptyLines: true,
                        dynamicTyping: true,
                    })
                    console.log(parsed)
                    // setCSVdata(parsed.data)
                    const res = parsed.data.map(obj => obj.residue_name)
                    setMapped(res)
                    // console.log(res)
                })
                .catch((error) => console.error('CSV load error:', error))
        }, [csv_url])

    useEffect(() => {
        if (!clusteringUrl) return
        fetch(`http://localhost:3000${clusteringUrl}`)
            .then((res) => res.json())
            .then((data) => {
                setClusteringData(data)
                const numClusters = Object.keys(data).length
                setClusterColors(generateClusterColors(numClusters))
            })
            .catch((err) => console.error('Clustering data error:', err))
    }, [clusteringUrl])

    useEffect(() => {
        let stage

        loadNGL().then((NGL) => {
            stage = new NGL.Stage(viewerRef.current, {
                backgroundColor: 'white',
            })
            stage.setParameters({ backgroundColor: null })

            stage
                .loadFile(`http://localhost:3000${pdbUrl}`, { name: 'protein' })
                .then((o) => {
                    o.addRepresentation('cartoon', {
                        opacity: 0.3,
                        color: 'white',
                    })
                    o.addRepresentation('line', {
                        sele: 'backbone',
                        color: 'green',
                    })

                    Object.entries(clusteringData).forEach(
                        ([clusterId, residues], i) => {
                            const seleString = residues
                                .map((r) => `${r.chain}:${r.residue}`)
                                .join(' OR ')

                            const labelSele = residues
                                .map((r) => `${r.chain}:${r.residue}`)
                                .join(' OR ')

                            o.addRepresentation('ball+stick', {
                                sele: seleString,
                                color: clusterColors[i],
                                name: clusterId,
                            })

                            o.addRepresentation('label', {
                                sele: labelSele,
                                labelType: 'residue',
                                color: clusterColors[i],
                                zOffset: 1.5,
                                scale: 1.5,
                                labelFontSize: 16,
                                showBackground: true,
                                backgroundColor: 'black',
                                backgroundOpacity: 0.6,
                            })
                        }
                    )

                    stage.autoView()
                })
                .catch((err) => console.error('Protein load error:', err))

            if (centroidsUrl) {
                stage
                    .loadFile(`http://localhost:3000${centroidsUrl}`, {
                        name: 'centroids',
                    })
                    .then((o) => {
                        o.addRepresentation('spacefill', {
                            radiusScale: 0.5,
                            colorScheme: 'bfactor',
                            colorScale: 'rainbow',
                        })
                    })
            }

            stage.setSpin(false)
            window.addEventListener('resize', stage.handleResize)
        })

        return () => {
            if (stage) {
                stage.removeAllComponents()
                window.removeEventListener('resize', stage.handleResize)
            }
        }
    }, [pdbUrl, centroidsUrl, clusteringData, clusterColors])

    return (
        <div className="rounded-xl bg-white/10 p-6 shadow-md backdrop-blur">
            <h3 className="mb-4 text-2xl font-semibold text-[#1e3c72]">
                🧬 Protein 3D Structure
            </h3>

            <p className="text-sm text-[#1e3c72]">
                Visual representation of the predicted 3D structure for this
                protein. The backbone is highlighted in green, and prion-like
                cluster regions are shown as color-coded spheres with residue
                labels.
            </p>

            {Object.keys(clusteringData).length > 0 && (
                <div className="mt-4 rounded-md bg-blue-50 p-6 text-sm text-[#1e3c72] shadow-sm">
                    <h2 className="mb-4 font-semibold text-xl">Cluster Legend</h2>
                    <div className="grid grid-cols-1 gap-2 md:grid-cols-2 md:gap-4">
                        {Object.entries(clusteringData).map(
                            ([clusterId, residues], i) => (
                                <div
                                    key={clusterId}
                                    className="flex items-start gap-2"
                                >
                                    
                                    <span
                                        className="mt-1 inline-block h-3 w-3 rounded-full"
                                        style={{
                                            backgroundColor: clusterColors[i],
                                        }}
                                    ></span>
                                    <div>
                                        <span className="text-sm font-medium">
                                            {clusterId
                                                .replace('_', ' ')
                                                .toUpperCase()}
                                        </span>
                                        <span className="block text-xs text-gray-600">
                                            {residues
                                                .map(
                                                    (r) =>
                                                        `${mapped[r.residue - 1]}${r.residue}`
                                                )
                                                .join(', ')}
                                        </span>
                                    </div>
                                </div>
                            )
                        )}
                    </div>
                </div>
            )}
            <div
                ref={viewerRef}
                style={{
                    width: '100%',
                    height: '500px',
                    backgroundColor: 'transparent',
                }}
                className="mt-4 rounded-lg border border-white/20 shadow-inner"
            />
        </div>
    )
}
