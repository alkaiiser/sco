import assert from 'node:assert/strict';
import test from 'node:test';
import { RESTORE_ROLE_NAMES } from '../../scripts/runtime-role-names.mjs';

test('restore preparation includes every least-privilege migration owner role', () => {
  const requiredRoles = [
    'sco_partner_admission_gateway_owner',
    'sco_internal_gateway_owner',
    'sco_verify_gateway_owner',
    'sco_verify_partner_read_owner',
    'sco_disclosure_gateway_owner',
    'sco_document_policy_gateway_owner',
    'sco_procurement_intelligence_gateway_owner',
    'sco_service_access_gateway_owner',
    'sco_workspace_gateway_owner',
    'sco_candidate_integrity_owner',
    'sco_collaboration_gateway_owner',
  ];

  assert.deepEqual(requiredRoles.filter((role) => !RESTORE_ROLE_NAMES.includes(role)), []);
});
