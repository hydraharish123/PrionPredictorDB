export async function loadNGL() {
    if (window.NGL) return window.NGL
    await import('https://unpkg.com/ngl@latest/dist/ngl.js')
    return window.NGL
}
