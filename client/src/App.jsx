import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Homepage from './pages/Homepage'
import Database from './pages/Database'

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Homepage />} />
                <Route path="/database" element={<Database />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
