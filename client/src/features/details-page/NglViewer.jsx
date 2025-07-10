import { useRef, useEffect } from 'react'
import { loadNGL } from '../../utils/loadNGL'

export function NglViewer({ pdbUrl, centroidsUrl }) {
    const viewerRef = useRef()

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
                    stage.autoView()
                })
                .catch((err) => {
                    console.error('Protein load error:', err)
                })

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
    }, [pdbUrl, centroidsUrl])

    return (
        <div className="mt-6">
            <h3 className="mb-2 text-lg font-bold text-white">3D Structure</h3>
            <div
                ref={viewerRef}
                style={{
                    width: '100%',
                    height: '500px',
                    backgroundColor: 'transparent',
                }}
                className="rounded border border-white"
            />
        </div>
    )
}
