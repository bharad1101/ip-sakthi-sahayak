import { useEffect, useMemo, useRef, useState } from "react";

import {
  Upload,
  Search,
  Leaf,
  FlaskConical,
  Package,
  MapPin,
  ShieldAlert,
  Lightbulb,
  Clock,
  X,
  Loader2,
  ScanSearch,
  Database,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  GitCompareArrows
} from "lucide-react";

import "./App.css";

import { LANGUAGES, getStrings } from "./i18n";


const API_URL = "http://127.0.0.1:8000";


function CategoryIcon({ categoryKey, fallbackCategory }) {

  const category =
    categoryKey ||
    fallbackCategory
      ?.toLowerCase() ||
    "";

  if (
    category.includes("product") ||
    category === "product"
  ) {

    return <Package size={25} />;

  }

  if (
    category.includes("component") ||
    category === "component"
  ) {

    return <FlaskConical size={25} />;

  }

  return <Leaf size={25} />;

}


function App() {

  const [mode, setMode] = useState("image");

  const [lang, setLang] = useState(
    () => localStorage.getItem("ipsakthi_lang") || "en"
  );

  const [selectedFile, setSelectedFile] = useState(null);

  const [previewUrl, setPreviewUrl] = useState("");

  const [searchText, setSearchText] = useState("");

  const [suggestions, setSuggestions] = useState([]);

  const [items, setItems] = useState({
    plants: [],
    components: [],
    products: []
  });

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const fileInputRef = useRef(null);

  const t = useMemo(() => getStrings(lang), [lang]);


  // ========================================================
  // LOAD AVAILABLE ITEMS (language aware)
  // ========================================================

  useEffect(() => {

    fetch(`${API_URL}/api/items?lang=${lang}`)
      .then(response => response.json())
      .then(data => {

        setItems(data);

      })
      .catch(() => {

        console.log(
          "Could not load prototype item database."
        );

      });

  }, [lang]);


  // ========================================================
  // LANGUAGE
  // ========================================================

  const changeLanguage = (code) => {

    setLang(code);

    localStorage.setItem("ipsakthi_lang", code);

    setSuggestions([]);

    setResult(null);

    setError("");

  };


  // ========================================================
  // RESET RESULTS WHEN SWITCHING MODE
  // ========================================================

  const switchMode = (newMode) => {

    setMode(newMode);

    setResult(null);

    setError("");

    setSearchText("");

    setSuggestions([]);

  };


  // ========================================================
  // FILE SELECTION
  // ========================================================

  const handleFileSelect = (event) => {

    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    setSelectedFile(file);

    setPreviewUrl(
      URL.createObjectURL(file)
    );

    setResult(null);

    setError("");

  };


  // ========================================================
  // REMOVE IMAGE
  // ========================================================

  const removeImage = () => {

    setSelectedFile(null);

    setPreviewUrl("");

    setResult(null);

    setError("");

    if (fileInputRef.current) {

      fileInputRef.current.value = "";

    }

  };


  // ========================================================
  // SEARCH SUGGESTIONS
  // ========================================================

  const toOption = (entry, type) => (

    typeof entry === "string"
      ? { key: entry, name: entry, type }
      : { ...entry, type }

  );

  const handleSearchChange = (value) => {

    setSearchText(value);

    setResult(null);

    setError("");

    const query =
      value.toLowerCase().trim();

    if (!query) {

      setSuggestions([]);

      return;
    }

    const combined = [

      ...(items.plants || []).map(entry =>
        toOption(entry, t.typePlant)
      ),

      ...(items.components || []).map(entry =>
        toOption(entry, t.typeComponent)
      ),

      ...(items.products || []).map(entry =>
        toOption(entry, t.typeProduct)
      )

    ];

    const filtered =
      combined.filter(item =>
        item.name
          .toLowerCase()
          .includes(query) ||
        (item.key || "")
          .toLowerCase()
          .includes(query)
      );

    setSuggestions(
      filtered.slice(0, 8)
    );

  };


  // ========================================================
  // SELECT SUGGESTION
  // ========================================================

  const selectSuggestion = (item) => {

    setSearchText(item.name);

    setSuggestions([]);

    setResult(null);

    setError("");

  };


  // ========================================================
  // ANALYZE IMAGE
  // ========================================================

  const analyzeImage = async () => {

    if (!selectedFile) {

      setError(t.errNoImage);

      return;
    }

    setLoading(true);

    setError("");

    setResult(null);

    try {

      const formData =
        new FormData();

      formData.append(
        "file",
        selectedFile
      );

      formData.append("lang", lang);

      const response =
        await fetch(
          `${API_URL}/api/analyze-image`,
          {
            method: "POST",
            body: formData
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          t.errImageFailed
        );

      }

      setResult(data);

    } catch (err) {

      setError(
        err.message ||
        t.errUnableImage
      );

    } finally {

      setLoading(false);

    }

  };


  // ========================================================
  // ANALYZE TEXT
  // ========================================================

  const analyzeText = async () => {

    if (!searchText.trim()) {

      setError(t.errEnterName);

      return;
    }

    setLoading(true);

    setError("");

    setResult(null);

    try {

      const response =
        await fetch(
          `${API_URL}/api/analyze?name=${encodeURIComponent(searchText)}&lang=${lang}`,
          {
            method: "POST"
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          t.errAnalyzeFailed
        );

      }

      setResult(data);

    } catch (err) {

      setError(
        err.message ||
        t.errUnableItem
      );

    } finally {

      setLoading(false);

    }

  };


  // ========================================================
  // GENERAL ANALYZE BUTTON
  // ========================================================

  const handleAnalyze = () => {

    if (mode === "image") {

      analyzeImage();

    } else {

      analyzeText();

    }

  };


  return (

    <div className="app">

      {/* ===================================================
          HEADER
      =================================================== */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">

            <Leaf size={25} />

          </div>

          <div>

            <h1>
              IP-SAKTHI Sahayak
            </h1>

            <p>
              {t.brandSubtitle}
            </p>

          </div>

        </div>


        <div className="header-actions">

          <div className="lang-switch" role="group" aria-label="Language">

            {LANGUAGES.map(option => (

              <button
                key={option.code}
                className={
                  lang === option.code
                    ? "lang-button active"
                    : "lang-button"
                }
                onClick={() =>
                  changeLanguage(option.code)
                }
              >
                {option.label}
              </button>

            ))}

          </div>


          <div className="local-ai">

            <span></span>

            {t.localAi}

          </div>

        </div>

      </header>


      <main className="container">


        {/* =================================================
            HERO
        ================================================= */}

        <section className="hero">

          <div>

            <span className="hero-label">
              {t.heroLabel}
            </span>

            <h2>
              {t.heroTitle}
            </h2>

            <p>
              {t.heroText}
            </p>

          </div>

        </section>


        {/* =================================================
            MODE TABS
        ================================================= */}

        <div className="mode-tabs">

          <button
            className={
              `mode ${
                mode === "image"
                  ? "active"
                  : ""
              }`
            }
            onClick={() =>
              switchMode("image")
            }
          >

            <ScanSearch size={18} />

            {t.tabImage}

          </button>


          <button
            className={
              `mode ${
                mode === "text"
                  ? "active"
                  : ""
              }`
            }
            onClick={() =>
              switchMode("text")
            }
          >

            <Search size={18} />

            {t.tabText}

          </button>

        </div>


        {/* =================================================
            IMAGE MODE
        ================================================= */}

        {mode === "image" && (

          <section className="upload-section">

            <div className="section-heading">

              <h2>
                {t.uploadHeading}
              </h2>

              <p>
                {t.uploadHint}
              </p>

            </div>


            {!selectedFile ? (

              <div
                className="upload-box"
                onClick={() =>
                  fileInputRef.current?.click()
                }
              >

                <div className="upload-icon">

                  <Upload size={30} />

                </div>

                <h3>
                  {t.uploadTitle}
                </h3>

                <p>
                  {t.uploadFormats}
                </p>

                <span className="upload-button">
                  {t.chooseImage}
                </span>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  onChange={handleFileSelect}
                  style={{
                    display: "none"
                  }}
                />

              </div>

            ) : (

              <div className="preview-area">

                <div className="preview-card">

                  <img
                    src={previewUrl}
                    alt="Uploaded"
                  />

                  <button
                    className="remove-image"
                    onClick={removeImage}
                    title="Remove image"
                  >

                    <X size={18} />

                  </button>

                </div>


                <div className="preview-actions">

                  <button
                    className="primary-button"
                    onClick={handleAnalyze}
                    disabled={loading}
                  >

                    {loading ? (

                      <>
                        <Loader2
                          size={18}
                          className="spin"
                        />

                        {t.analyzing}

                      </>

                    ) : (

                      <>
                        <Sparkles size={18} />

                        {t.analyzeImage}

                      </>

                    )}

                  </button>


                  <button
                    className="secondary-button"
                    onClick={() =>
                      fileInputRef.current?.click()
                    }
                  >

                    <Upload size={17} />

                    {t.chooseAnother}

                  </button>

                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    onChange={handleFileSelect}
                    style={{
                      display: "none"
                    }}
                  />

                </div>

              </div>

            )}

          </section>

        )}


        {/* =================================================
            TEXT MODE
        ================================================= */}

        {mode === "text" && (

          <section className="search-section">

            <div className="section-heading">

              <h2>
                {t.searchHeading}
              </h2>

              <p>
                {t.searchHint}
              </p>

            </div>


            <div className="search-box">

              <Search size={20} />

              <input
                value={searchText}
                onChange={(event) =>
                  handleSearchChange(
                    event.target.value
                  )
                }
                placeholder={t.searchPlaceholder}
              />


              {searchText && (

                <button
                  className="clear-button"
                  onClick={() => {

                    setSearchText("");

                    setSuggestions([]);

                    setResult(null);

                  }}
                >

                  <X size={17} />

                </button>

              )}

            </div>


            {suggestions.length > 0 && (

              <div className="suggestions">

                {suggestions.map(
                  (item, index) => (

                    <button
                      key={`${item.key || item.name}-${index}`}
                      onClick={() =>
                        selectSuggestion(item)
                      }
                    >

                      {item.type === t.typePlant && (
                        <Leaf size={17} />
                      )}

                      {item.type === t.typeComponent && (
                        <FlaskConical size={17} />
                      )}

                      {item.type === t.typeProduct && (
                        <Package size={17} />
                      )}

                      <span>
                        {item.name}
                      </span>

                      <small>
                        {item.type}
                      </small>

                    </button>

                  )
                )}

              </div>

            )}


            <button
              className="primary-button"
              onClick={handleAnalyze}
              disabled={
                loading ||
                !searchText.trim()
              }
              style={{
                width: "100%",
                marginTop: "14px"
              }}
            >

              {loading ? (

                <>
                  <Loader2
                    size={18}
                    className="spin"
                  />

                  {t.analyzing}

                </>

              ) : (

                <>
                  <Sparkles size={18} />

                  {t.analyze}

                </>

              )}

            </button>

          </section>

        )}


        {/* =================================================
            ERROR
        ================================================= */}

        {error && (

          <div className="error-card">

            <AlertTriangle size={20} />

            <div>

              <strong>
                {t.errorTitle}
              </strong>

              <p>
                {error}
              </p>

            </div>

          </div>

        )}


        {/* =================================================
            LOADING
        ================================================= */}

        {loading && (

          <div className="loading-card">

            <Loader2
              size={23}
              className="spin"
            />

            <div>

              <strong>
                {t.loadingTitle}
              </strong>

              <p>
                {t.loadingText}
              </p>

            </div>

          </div>

        )}


        {/* =================================================
            RESULTS
            This ONLY renders when result exists.
        ================================================= */}

        {result?.success && result?.data && (

          <section className="results-section">


            <div className="results-heading">

              <div>

                <span>
                  {t.resultsLabel}
                </span>

                <h2>
                  {t.resultsTitle}
                </h2>

              </div>

            </div>


            {/* =============================================
                AI IDENTIFICATION
            ============================================= */}

            {result.source === "image" && (

              <div className="identification-card">

                <div className="identified-icon">

                  <CheckCircle2 size={27} />

                </div>

                <div>

                  <span>
                    {t.aiIdLabel}
                  </span>

                  <h3>
                    {result.identified_name}
                  </h3>

                  <p>
                    {t.aiIdCompleted}
                  </p>

                  {result.model_confidence !== undefined && (

                    <small>
                      {t.visionConfidence}
                      {" "}
                      {result.model_confidence}%
                    </small>

                  )}

                </div>

              </div>

            )}


            {/* =============================================
                TITLE
            ============================================= */}

            <div className="details">


              <div className="title-card">

                <div className="title-icon">

                  <CategoryIcon
                    categoryKey={
                      result.category_key
                    }
                    fallbackCategory={
                      result.data.category
                    }
                  />

                </div>

                <div>

                  <span className="eyebrow">

                    {result.data.category}

                  </span>

                  <h2>
                    {result.data.name}
                  </h2>

                  {result.data.scientific_name && (

                    <p className="scientific">
                      {result.data.scientific_name}
                    </p>

                  )}

                </div>

              </div>


              {/* =========================================
                  BASIC INFORMATION
              ========================================= */}

              <div className="card">

                <h3>
                  <Database size={18} />

                  {t.basicInfo}
                </h3>


                <div className="object-grid">

                  {result.data.family && (

                    <div className="object-item">

                      <span>
                        {t.family}
                      </span>

                      <strong>
                        {result.data.family}
                      </strong>

                    </div>

                  )}


                  {result.data.source && (

                    <div className="object-item">

                      <span>
                        {t.source}
                      </span>

                      <strong>
                        {result.data.source}
                      </strong>

                    </div>

                  )}


                  {result.data.rarity && (

                    <div className="object-item">

                      <span>
                        {t.availability}
                      </span>

                      <strong>
                        {result.data.rarity}
                      </strong>

                    </div>

                  )}


                  {result.data.confidence && (

                    <div className="object-item">

                      <span>
                        {t.knowledgeMatch}
                      </span>

                      <strong>
                        {result.data.confidence}%
                      </strong>

                    </div>

                  )}

                </div>

              </div>


              {/* =========================================
                  PARTS / COMPONENTS
              ========================================= */}

              {(result.data.parts ||
                result.data.components) && (

                <div className="card">

                  <h3>

                    <FlaskConical size={18} />

                    {t.partsTitle}

                  </h3>


                  <ul className="info-list">

                    {(
                      result.data.parts ||
                      result.data.components
                    ).map(
                      (item, index) => (

                        <li key={index}>
                          {item}
                        </li>

                      )
                    )}

                  </ul>

                </div>

              )}


              {/* =========================================
                  LOCATION
              ========================================= */}

              {result.data.locations && (

                <div className="card">

                  <h3>

                    <MapPin size={18} />

                    {t.distribution}

                  </h3>


                  <ul className="info-list">

                    {result.data.locations.map(
                      (location, index) => (

                        <li key={index}>
                          {location}
                        </li>

                      )
                    )}

                  </ul>

                </div>

              )}


              {/* =========================================
                  GROWTH TIME
              ========================================= */}

              {result.data.growth_time && (

                <div className="card">

                  <h3>

                    <Clock size={18} />

                    {t.growthTitle}

                  </h3>


                  <div
                    className="object-grid"
                    style={{
                      marginBottom: "20px"
                    }}
                  >

                    <div className="object-item">

                      <span>
                        {t.overallTimeline}
                      </span>

                      <strong>
                        {result.data.growth_time}
                      </strong>

                    </div>

                  </div>


                  {result.data.growth_timeline && (

                    <div className="growth-timeline">

                      {result.data.growth_timeline.map(
                        (stage, index) => (

                          <div
                            className="growth-stage"
                            key={index}
                          >

                            <div className="timeline-dot">
                              {index + 1}
                            </div>

                            <div>

                              <strong>
                                {stage.stage}
                              </strong>

                              <p>
                                {stage.duration}
                              </p>

                            </div>

                          </div>

                        )
                      )}

                    </div>

                  )}

                </div>

              )}


              {/* =========================================
                  TRADITIONAL USES
              ========================================= */}

              {result.data.traditional_uses && (

                <div className="card">

                  <h3>

                    <Leaf size={18} />

                    {t.traditionalTitle}

                  </h3>


                  <ul className="info-list">

                    {result.data.traditional_uses.map(
                      (use, index) => (

                        <li key={index}>
                          {use}
                        </li>

                      )
                    )}

                  </ul>

                </div>

              )}


              {/* =========================================
                  SAFETY
              ========================================= */}

              {result.data.safety && (

                <div className="card safety-card">

                  <h3>

                    <ShieldAlert size={18} />

                    {t.safetyTitle}

                  </h3>


                  <div className="object-grid">

                    {result.data.safety.level && (

                      <div className="object-item">

                        <span>
                          {t.assessment}
                        </span>

                        <strong>
                          {result.data.safety.level}
                        </strong>

                      </div>

                    )}


                    {result.data.safety.toxicity && (

                      <div className="object-item">

                        <span>
                          {t.toxicity}
                        </span>

                        <strong>
                          {result.data.safety.toxicity}
                        </strong>

                      </div>

                    )}


                    {result.data.safety.adverse_effects && (

                      <div className="object-item">

                        <span>
                          {t.adverseEffects}
                        </span>

                        <strong>
                          {result.data.safety.adverse_effects}
                        </strong>

                      </div>

                    )}


                    {result.data.safety.interactions && (

                      <div className="object-item">

                        <span>
                          {t.interactions}
                        </span>

                        <strong>
                          {result.data.safety.interactions}
                        </strong>

                      </div>

                    )}

                  </div>

                </div>

              )}


              {/* =========================================
                  MEDICINAL COMPARISONS
              ========================================= */}

              {result.data.medicinal_comparisons?.length > 0 && (

                <div className="card comparison-card">

                  <h3>

                    <GitCompareArrows size={18} />

                    {t.comparisonsTitle}

                  </h3>


                  <div className="comparison-list">

                    {result.data.medicinal_comparisons.map(
                      (comparison, index) => (

                        <div
                          className="comparison-item"
                          key={index}
                        >

                          <div className="comparison-header">

                            <span>
                              {t.comparedWith}
                            </span>

                            <strong>
                              {comparison.compared_with}
                            </strong>

                          </div>


                          <div className="comparison-body">

                            <p>

                              <small>
                                {t.sharedLabel}
                              </small>

                              {comparison.shared}

                            </p>


                            <p>

                              <small>
                                {t.differenceLabel}
                              </small>

                              {comparison.difference}

                            </p>

                          </div>

                        </div>

                      )
                    )}

                  </div>

                </div>

              )}


              {/* =========================================
                  INNOVATION
              ========================================= */}

              {result.data.innovation && (

                <div className="card innovation-card">

                  <h3>

                    <Lightbulb size={18} />

                    {t.innovationTitle}

                  </h3>


                  <ul className="info-list">

                    {result.data.innovation.map(
                      (idea, index) => (

                        <li key={index}>
                          {idea}
                        </li>

                      )
                    )}

                  </ul>

                </div>

              )}


              {/* =========================================
                  IMAGE REASON
              ========================================= */}

              {result.visual_reason && (

                <div className="card">

                  <h3>

                    <ScanSearch size={18} />

                    {t.visualNotes}

                  </h3>

                  <p>
                    {result.visual_reason}
                  </p>

                </div>

              )}


              {/* =========================================
                  DISCLAIMER
              ========================================= */}

              <div className="disclaimer">

                <strong>
                  {t.disclaimerStrong}
                </strong>{" "}

                {t.disclaimerText}

              </div>


            </div>

          </section>

        )}


        {/* =================================================
            UNKNOWN / NOT FOUND RESULT
        ================================================= */}

        {result &&
         !result.success && (

          <div className="card unknown-card">

            <h3>

              <AlertTriangle size={18} />

              {t.unknownTitle}

            </h3>

            {(result.identified_name ||
              result.source === "image") && (

              <p>

                {t.unknownLead}

                <strong>
                  {" "}
                  {result.identified_name || t.unknownItem}
                </strong>

              </p>

            )}

            <p style={{ marginTop: "8px" }}>

              {result.message || t.unknownText}

            </p>

          </div>

        )}


      </main>


      {/* ===================================================
          FOOTER
      =================================================== */}

      <footer>

        <p>
          {t.footerLeft}
        </p>

        <p>
          {t.footerRight}
        </p>

      </footer>

    </div>

  );

}


export default App;
