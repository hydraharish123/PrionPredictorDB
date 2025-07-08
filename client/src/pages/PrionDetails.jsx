import { useParams } from 'react-router-dom'

function PrionDetails() {
    const { id } = useParams()
    return <div>{id}</div>
}

export default PrionDetails
