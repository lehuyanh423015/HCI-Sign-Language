import { Navigate, Route, Routes } from 'react-router-dom';
import { LessonPage } from '../features/lessons/LessonPage';
import { QuizPage } from '../features/quiz/QuizPage';
import { ReviewPage } from '../features/review/ReviewPage';
import { TechnicalViewerPage } from '../features/technical/TechnicalViewerPage';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LessonPage />} />
      <Route path="/quiz" element={<QuizPage />} />
      <Route path="/review" element={<ReviewPage />} />
      <Route path="/technical-viewer" element={<TechnicalViewerPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
