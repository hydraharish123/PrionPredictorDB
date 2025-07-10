import Papa from 'papaparse'
import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'

function AggreScan3dChart({ csv_url }) {
    const [csvData, setCSVdata] = useState([])
    useEffect(() => {
        fetch(`http://localhost:3000${csv_url}`)
            .then((response) => response.text())
            .then((csvText) => {
                const parsed = Papa.parse(csvText, {
                    header: true, // use first row as keys
                    skipEmptyLines: true,
                    dynamicTyping: true,
                })
                
                setCSVdata(parsed.data)
            })
            .catch((error) => console.error('CSV load error:', error))
    }, [csv_url])
    return (
        <div className="w-full">
            <div className="my-4 rounded-lg bg-blue-50 p-4 text-sm text-[#1e3c72] shadow-sm">
                <h3 className="mb-2 text-base font-semibold">
                    Aggregation and Aggrescan3D (A3D)
                </h3>
                <p className="mb-2">
                    Protein aggregation refers to the process by which misfolded
                    proteins self-associate into insoluble assemblies, often
                    leading to cellular dysfunction and disease. In prion-like
                    proteins, aggregation-prone regions can propagate
                    misfolding, contributing to neurodegenerative conditions
                    like ALS and Alzheimer's.
                </p>
                <p>
                    <strong>Aggrescan3D (A3D)</strong> is a structure-based tool
                    that predicts aggregation propensity by analyzing the 3D
                    conformation of proteins. Unlike sequence-only predictors,
                    A3D accounts for spatial context, surface accessibility, and
                    hydrophobic clustering—making it especially valuable for
                    assessing the aggregation risk of
                    <strong> prion-like domains (PrLDs)</strong> within folded
                    structures.
                </p>
            </div>

            {csvData.length > 0 && (
                <Plot
                    data={[
                        {
                            x: csvData.map((d) => d.residue),
                            y: csvData.map((d) => parseFloat(d.score)),
                            type: 'scatter',
                            mode: 'lines+markers',
                            line: { color: 'steelblue', width: 1 },
                            marker: { size: 6, color: 'steelblue' },
                            hoverinfo: 'skip',
                            showlegend: false,
                        },
                        // Residues with score > 0 (labels)
                        {
                            x: csvData
                                .filter((d) => parseFloat(d.score) > 0)
                                .map((d) => d.residue),
                            y: csvData
                                .filter((d) => parseFloat(d.score) > 0)
                                .map((d) => parseFloat(d.score)),
                            type: 'scatter',
                            mode: 'text',
                            text: csvData
                                .filter((d) => parseFloat(d.score) > 0)
                                .map((d) => `${d.residue_name}${d.residue}`),
                            textposition: 'top center',
                            textfont: {
                                size: 10,
                                color: 'rgba(100,100,100,0.6)',
                            },

                            showlegend: false,
                        },
                        // Dashed line at y=0
                        {
                            x: [
                                csvData[0].residue,
                                csvData[csvData.length - 1].residue,
                            ],
                            y: [0, 0],
                            mode: 'lines',
                            line: {
                                dash: 'dash',
                                color: 'gray',
                                width: 1,
                            },
                            hoverinfo: 'skip',
                            showlegend: false,
                        },
                    ]}
                    layout={{
                        title: 'Aggrescan3D Plot',
                        autosize: true,
                        margin: { l: 50, r: 30, b: 50, t: 60 },
                    }}
                    useResizeHandler={true}
                    style={{ width: '100%', height: '500px' }}
                    config={{ responsive: true }}
                />
            )}
        </div>
    )
}

export default AggreScan3dChart
