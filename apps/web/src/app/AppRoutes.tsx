import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AccountPage, RequireAccount } from './Account';
import { AdminDashboard } from '../features/admin/AdminDashboard';
import { AdminPage } from '../features/admin/AdminPage';
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
  const demo = new URLSearchParams(location.search).get('demo') === '1';
  const guard = (view: React.ReactNode) => demo ? view : <RequireAccount>{view}</RequireAccount>;
  return (
    <Routes>
      <Route path="/login" element={<AccountPage key="login" registering={false}/>}/>
      <Route path="/register" element={<AccountPage key="register" registering/>}/>
      <Route path="/admin" element={<RequireAccount admin><AdminDashboard/></RequireAccount>}/>
      <Route path="/admin/catalog" element={<RequireAccount admin><AdminPage/></RequireAccount>}/>
      <Route path="/" element={<Home />} />
      <Route path="/lessons" element={<Library />} />
      <Route path="/lessons/:id" element={<RequireAccount><LessonPage /></RequireAccount>} />
      <Route path="/quiz" element={guard(<QuizPage key={location.search} />)} />
      <Route path="/results" element={guard(<ResultsPage />)} />
      <Route path="/review" element={guard(<ReviewPage />)} />
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
