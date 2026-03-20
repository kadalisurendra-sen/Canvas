import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { AdminLayout } from './components/layout/AdminLayout';
import { AuthGuard } from './components/guards/AuthGuard';
import { RoleGuard } from './components/guards/RoleGuard';
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
        {/* All roles */}
        <Route path="/templates" element={<TemplateManagementPage />} />

        {/* Admin only */}
        <Route path="/analytics" element={
          <RoleGuard roles={['system_admin', 'admin']}>
            <AnalyticsPage />
          </RoleGuard>
        } />

        {/* Admin only */}
        <Route path="/users" element={
          <RoleGuard roles={['system_admin', 'admin']}>
            <UsersPage />
          </RoleGuard>
        } />
        <Route path="/settings" element={
          <RoleGuard roles={['system_admin', 'admin']}>
            <SettingsPage />
          </RoleGuard>
        } />
        <Route path="/settings/:tenantId" element={
          <RoleGuard roles={['system_admin', 'admin']}>
            <SettingsPage />
          </RoleGuard>
        } />
        <Route path="/master-data" element={
          <RoleGuard roles={['system_admin', 'admin']}>
            <MasterDataPage />
          </RoleGuard>
        } />

        {/* Template Wizard — admin only */}
        <Route path="/templates/new" element={
          <RoleGuard roles={['system_admin', 'admin']}>
            <WizardLayout />
          </RoleGuard>
        }>
          <Route index element={<WizardStep1 />} />
          <Route path="step2" element={<WizardStep2 />} />
          <Route path="step3" element={<WizardStep3 />} />
          <Route path="step4" element={<WizardStep4 />} />
          <Route path="step5" element={<WizardStep5 />} />
        </Route>
        <Route path="/templates/:id/edit" element={
          <RoleGuard roles={['system_admin', 'admin']}>
            <WizardLayout />
          </RoleGuard>
        }>
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
