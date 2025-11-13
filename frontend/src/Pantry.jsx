import { useEffect, useRef, useState } from "react";
import "./Pantry.css";

export default function Pantry() {
  const [items, setItems] = useState([]);
  const [query, setQuery] = useState("");
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState("");
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const rafRef = useRef(0);
  const detectorRef = useRef(null);
  const [manualCode, setManualCode] = useState("");

  // Start camera scanning
  const startScan = async () => {
    setError("");
    const supported =
      "BarcodeDetector" in window &&
      typeof window.BarcodeDetector === "function";

    if (!supported) {
      setError(
        "Barcode scanning not supported in this browser. Use Chrome/Edge, or add manually below."
      );
      return;
    }

    try {
      detectorRef.current = new window.BarcodeDetector({
        formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128", "code_39"],
      });

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      });
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setScanning(true);
      scanLoop();
    } catch (e) {
      console.error(e);
      setError("Could not access the camera. Check permissions and try again.");
    }
  };

  // Stop scanning
  const stopScan = () => {
    cancelAnimationFrame(rafRef.current);
    setScanning(false);
    if (videoRef.current) videoRef.current.pause();
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  };

  // Cleanup
  useEffect(() => {
    return () => stopScan();
  }, []);

  // Detection loop
  const scanLoop = async () => {
    if (!videoRef.current || !detectorRef.current) return;

    try {
      const barcodes = await detectorRef.current.detect(videoRef.current);
      if (barcodes && barcodes.length) {
        const code = barcodes[0].rawValue || "";
        handleDetectedBarcode(code);
        stopScan();
        return;
      }
    } catch (e) {
      // Ignore temporary decode errors
    }
    rafRef.current = requestAnimationFrame(scanLoop);
  };

  // Handle detected barcode
  const handleDetectedBarcode = async (barcode) => {
    const product = await mockLookup(barcode);
    const id = `${barcode}-${Date.now()}`;
    setItems((prev) => [{ id, barcode, ...product }, ...prev]);
  };

  // Mock product lookup
  async function mockLookup(barcode) {
    const known = {
      "012345678905": { title: "Spaghetti Pasta", brand: "Barilla" },
      "04963406": { title: "Tomato Sauce", brand: "Hunt's" },
      "036000291452": { title: "All-Purpose Flour", brand: "King Arthur" },
    };
    return known[barcode] || {
      title: `Item ${barcode.slice(-4)}`,
      brand: "Unknown Brand",
    };
  }

  const removeItem = (id) =>
    setItems((prev) => prev.filter((it) => it.id !== id));

  const filtered = items.filter((it) =>
    (it.title + " " + (it.brand || "") + " " + (it.barcode || ""))
      .toLowerCase()
      .includes(query.toLowerCase())
  );

  const addManual = async (e) => {
    e.preventDefault();
    if (!manualCode.trim()) return;
    await handleDetectedBarcode(manualCode.trim());
    setManualCode("");
  };

  return (
    <main className="page pantry-page">
      <div className="container">
        {/* Header */}
        <div className="pantry-header">
          <h1 className="page__title">Your Pantry</h1>
          <p className="page__subtitle">
            Scan a barcode to add items. Search to quickly find what you have.
          </p>

          {/* Search bar */}
          <section className="search-section">
            <div className="searchbar">
              <span className="searchbar__icon" aria-hidden="true">
                🔎
              </span>
              <input
                className="searchbar__input"
                placeholder="Search pantry…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
          </section>

          {/* Scan / Stop Button */}
          <div className="scan-controls">
            {!scanning ? (
              <button className="btn btn--solid" onClick={startScan}>
                📷 Scan Barcode
              </button>
            ) : (
              <button className="btn btn--ghost" onClick={stopScan}>
                ✖ Stop
              </button>
            )}
          </div>
        </div>

        {/* Scanner preview */}
        {scanning && (
          <section className="scanner-section">
            <div className="card scanner-card">
              <video ref={videoRef} autoPlay playsInline muted />
            </div>
          </section>
        )}

        {/* Error */}
        {error && (
          <div className="error-section">
            <p className="error-message">{error}</p>
          </div>
        )}

        {/* Manual Add */}
        {error && (
          <section className="manual-add">
            <form onSubmit={addManual} className="card manual-form">
              <input
                className="searchbar__input"
                placeholder="Enter barcode manually"
                value={manualCode}
                onChange={(e) => setManualCode(e.target.value)}
              />
              <button className="btn btn--solid sm" type="submit">
                Add
              </button>
            </form>
          </section>
        )}

        {/* Pantry Items */}
        <section className="pantry-grid">
          {filtered.length === 0 ? (
            <div className="card empty-state">
              {items.length === 0 ? (
                <p>
                  Your pantry is empty. Click <b>Scan Barcode</b> to add your first item.
                </p>
              ) : (
                <p className="empty-message">No items match "{query}".</p>
              )}
            </div>
          ) : (
            filtered.map((it) => (
              <article key={it.id} className="card pantry-item">
                <div className="pantry-item__content">
                  <div className="pantry-item__info">
                    <h3>{it.title}</h3>
                    <p>
                      {it.brand || "—"} • <span>Barcode: {it.barcode}</span>
                    </p>
                  </div>
                  <button
                    className="btn btn--ghost sm"
                    onClick={() => removeItem(it.id)}
                  >
                    Remove
                  </button>
                </div>
              </article>
            ))
          )}
        </section>
      </div>
    </main>
  );
}