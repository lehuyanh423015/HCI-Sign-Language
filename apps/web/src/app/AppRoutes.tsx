import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Home, Library, LessonPage } from "../features/lessons/LessonPage";
import {
  DemoPage,
  DemoReplay,
  QuizPage,
  ResultsPage,
} from "../features/quiz/QuizPage";
import { ReviewPage } from "../features/review/ReviewPage";
import { TechnicalViewerPage } from "../features/technical/TechnicalViewerPage";
import { TechnicalFacialViewerPage } from "../features/technical/TechnicalFacialViewerPage";
import { SignAnimationPreviewPage } from "../features/technical/SignAnimationPreviewPage";
export function AppRoutes() {
  const location = useLocation();
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/lessons" element={<Library />} />
      <Route path="/lessons/:id" element={<LessonPage />} />
      <Route path="/quiz" element={<QuizPage key={location.search} />} />
      <Route path="/results" element={<ResultsPage />} />
      <Route path="/review" element={<ReviewPage />} />
      <Route path="/demo" element={<DemoPage />} />
      <Route path="/demo/:id" element={<DemoReplay />} />
      <Route path="/technical-viewer" element={<TechnicalViewerPage />} />
      <Route
        path="/technical-facial-viewer"
        element={<TechnicalFacialViewerPage />}
      />
      <Route
        path="/technical-sign-preview"
        element={<SignAnimationPreviewPage />}
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
