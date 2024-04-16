-- 2020-05-29 09:20

CREATE INDEX iOpExecTimestampValue
  ON m_operation_execution (timestampValue);

-- 2020-06-25 11:35

ALTER TABLE m_acc_cert_campaign RENAME COLUMN definitionRef_type TO definitionRef_targetType;
ALTER TABLE m_acc_cert_campaign RENAME COLUMN ownerRef_type TO ownerRef_targetType;
ALTER TABLE m_acc_cert_definition RENAME COLUMN ownerRef_type TO ownerRef_targetType;
ALTER TABLE m_connector RENAME COLUMN connectorHostRef_type TO connectorHostRef_targetType;
ALTER TABLE m_object RENAME COLUMN creatorRef_type TO creatorRef_targetType;
ALTER TABLE m_object RENAME COLUMN modifierRef_type TO modifierRef_targetType;
ALTER TABLE m_object RENAME COLUMN tenantRef_type TO tenantRef_targetType;
ALTER TABLE m_report_output RENAME COLUMN reportRef_type TO reportRef_targetType;
ALTER TABLE m_resource RENAME COLUMN connectorRef_type TO connectorRef_targetType;
ALTER TABLE m_shadow RENAME COLUMN resourceRef_type TO resourceRef_targetType;
ALTER TABLE m_acc_cert_case RENAME COLUMN objectRef_type TO objectRef_targetType;
ALTER TABLE m_acc_cert_case RENAME COLUMN orgRef_type TO orgRef_targetType;
ALTER TABLE m_acc_cert_case RENAME COLUMN targetRef_type TO targetRef_targetType;
ALTER TABLE m_acc_cert_case RENAME COLUMN tenantRef_type TO tenantRef_targetType;
ALTER TABLE m_acc_cert_wi RENAME COLUMN performerRef_type TO performerRef_targetType;
ALTER TABLE m_assignment RENAME COLUMN creatorRef_type TO creatorRef_targetType;
ALTER TABLE m_assignment RENAME COLUMN modifierRef_type TO modifierRef_targetType;
ALTER TABLE m_assignment RENAME COLUMN orgRef_type TO orgRef_targetType;
ALTER TABLE m_assignment RENAME COLUMN resourceRef_type TO resourceRef_targetType;
ALTER TABLE m_assignment RENAME COLUMN targetRef_type TO targetRef_targetType;
ALTER TABLE m_assignment RENAME COLUMN tenantRef_type TO tenantRef_targetType;
ALTER TABLE m_case_wi RENAME COLUMN originalAssigneeRef_type TO originalAssigneeRef_targetType;
ALTER TABLE m_case_wi RENAME COLUMN performerRef_type TO performerRef_targetType;
ALTER TABLE m_operation_execution RENAME COLUMN initiatorRef_type TO initiatorRef_targetType;
ALTER TABLE m_operation_execution RENAME COLUMN taskRef_type TO taskRef_targetType;
ALTER TABLE m_task RENAME COLUMN objectRef_type TO objectRef_targetType;
ALTER TABLE m_task RENAME COLUMN ownerRef_type TO ownerRef_targetType;
ALTER TABLE m_abstract_role RENAME COLUMN ownerRef_type TO ownerRef_targetType;
ALTER TABLE m_case RENAME COLUMN objectRef_type TO objectRef_targetType;
ALTER TABLE m_case RENAME COLUMN parentRef_type TO parentRef_targetType;
ALTER TABLE m_case RENAME COLUMN requestorRef_type TO requestorRef_targetType;
ALTER TABLE m_case RENAME COLUMN targetRef_type TO targetRef_targetType;

-- 2020-08-19 10:55

ALTER TABLE m_focus ADD COLUMN passwordCreateTimestamp TIMESTAMP;
ALTER TABLE m_focus ADD COLUMN passwordModifyTimestamp TIMESTAMP;

-- MID-6037
ALTER TABLE m_service ADD CONSTRAINT uc_service_name UNIQUE (name_norm);

-- MID-6232
CREATE INDEX iAuditEventRecordEStageTOid
  ON m_audit_event (eventStage, targetOid);

-- policySituation belong to M_OBJECT
ALTER TABLE m_focus_policy_situation DROP CONSTRAINT fk_focus_policy_situation;
ALTER TABLE m_focus_policy_situation RENAME TO m_object_policy_situation;
ALTER TABLE m_object_policy_situation RENAME COLUMN focus_oid TO object_oid;
ALTER TABLE m_object_policy_situation
  ADD CONSTRAINT fk_object_policy_situation FOREIGN KEY (object_oid) REFERENCES m_object;
ALTER INDEX iFocusPolicySituationOid RENAME TO iObjectPolicySituationOid;

COMMIT;

-- 4.3+ Changes
-- MID-6417
ALTER TABLE m_operation_execution ADD COLUMN recordType INT4;

-- MID-3669
ALTER TABLE m_focus ADD COLUMN lockoutStatus INT4;

-- 4.4+ Changes
-- MID-7173
ALTER TABLE m_task ADD COLUMN schedulingState INT4;
ALTER TABLE m_task ADD COLUMN autoScalingMode INT4;
ALTER TABLE m_node ADD COLUMN operationalState INT4;

-- MID-7074

CREATE UNIQUE INDEX m_connector_typeVersion_key
    ON m_connector (connectorType, connectorVersion)
    WHERE connectorHostRef_targetOid IS NULL;
CREATE UNIQUE INDEX m_connector_typeVersionHost_key
    ON m_connector (connectorType, connectorVersion, connectorHostRef_targetOid)
    WHERE connectorHostRef_targetOid IS NOT NULL;


-- WRITE CHANGES ABOVE ^^
UPDATE m_global_metadata SET value = '4.4' WHERE name = 'databaseSchemaVersion';

-- MID-6974
UPDATE qrtz_job_details SET job_class_name = 'com.evolveum.midpoint.task.quartzimpl.run.JobExecutor'
    WHERE job_class_name = 'com.evolveum.midpoint.task.quartzimpl.execution.JobExecutor';

COMMIT;
