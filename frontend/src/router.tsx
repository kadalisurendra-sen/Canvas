import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { AdminLayout } from './components/layout/AdminLayout';
import { AuthGuard } from './components/guards/AuthGuard';
import { LoginPage } from './pages/LoginPage';
import { SignUpPage } from './pages/SignUpPage';
import { CallbackPage } from './pages/CallbackPage';
import { TemplateManagementPage } from './pages/TemplateManagementPage';
import { UsersPage } from './pages/UsersPage';
import { SettingsPage } from './pages/SettingsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { MasterDataPage } from './pages/MasterDataPage';
import { WizardLayout } from './pages/wizard/WizardLayout';
import { WizardStep1 } from './pages/wizard/WizardStep1';
import { WizardStep2 } from './pages/wizard/WizardStep2';
import { WizardStep3 } from './pages/wizard/WizardStep3';
import { WizardStep4 } from './pages/wizard/WizardStep4';
import { WizardStep5 } from './pages/wizard/WizardStep5';

export function AppRouter() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/auth/callback" element={<CallbackPage />} />

      {/* Protected routes */}
      <Route
        element={
          <AuthGuard>
            <AdminLayout />
          </AuthGuard>
        }
      >
        <Route path="/templates" element={<TemplateManagementPage />} />
        <Route path="/users" element={<UsersPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/master-data" element={<MasterDataPage />} />

        {/* Template Wizard routes */}
        <Route path="/templates/new" element={<WizardLayout />}>
          <Route index element={<WizardStep1 />} />
          <Route path="step2" element={<WizardStep2 />} />
          <Route path="step3" element={<WizardStep3 />} />
          <Route path="step4" element={<WizardStep4 />} />
          <Route path="step5" element={<WizardStep5 />} />
        </Route>
        <Route path="/templates/:id/edit" element={<WizardLayout />}>
          <Route index element={<WizardStep1 />} />
          <Route path="step2" element={<WizardStep2 />} />
          <Route path="step3" element={<WizardStep3 />} />
          <Route path="step4" element={<WizardStep4 />} />
          <Route path="step5" element={<WizardStep5 />} />
        </Route>
      </Route>

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/templates" replace />} />
      <Route path="*" element={<Navigate to="/templates" replace />} />
    </Routes>
  );
}
