import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Homepage from './pages/Homepage'
import Database from './pages/Database'
import PrionDetails from './pages/PrionDetails'

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Homepage />} />
                <Route path="/database" element={<Database />} />
                <Route path="/database/:id" element={<PrionDetails />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
