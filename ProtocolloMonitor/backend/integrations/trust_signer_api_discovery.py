class TrustSignerApiDiscovery:
    """Documentation-only placeholder for the Trust Signer discovery activity."""

    BASE_URL = "https://trustsigner.tipki.it/ITTCryptoClientWeb/rest/api/"

    def init_configuration(self):
        """Document the observed configuration bootstrap endpoint."""
        # Expected endpoint:
        #   GET /configuration/init
        #
        # Hypothesized HTTP method:
        #   GET
        #
        # Data to observe in Chrome DevTools Network:
        #   - status code and response schema;
        #   - version fields returned by the service;
        #   - license information returned by the service;
        #   - upload limits, allowed file types and size constraints;
        #   - activeVerification flag or equivalent verification availability;
        #   - signatureReasons list and how it is used later in signing flows;
        #   - whether request headers include session, CSRF, tenant or locale data.
        #
        # What is needed for SoluzioniOperative integration:
        #   - a safe way to read capability flags before enabling assisted flows;
        #   - documented meaning of license and upload constraints;
        #   - confirmation that reading this endpoint is allowed for integration;
        #   - behavior when configuration is unavailable or license is invalid.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")

    def list_files(self):
        """Document the observed temporary file listing endpoint."""
        # Expected endpoint:
        #   GET /files/list
        #
        # Hypothesized HTTP method:
        #   GET
        #
        # Data to observe in Chrome DevTools Network:
        #   - response schema for uploaded and signed files;
        #   - file identifiers and whether they are stable across page refreshes;
        #   - fields for original filename, MIME type, signed status and size;
        #   - whether entries are tied to browser cookies or server-side session;
        #   - whether signed files appear in the same list after completion;
        #   - expiration behavior for temporary files.
        #
        # What is needed for SoluzioniOperative integration:
        #   - a supported way to correlate a ProtocolloMonitor document with a
        #     Trust Signer temporary file id;
        #   - lifecycle rules for temporary files;
        #   - error handling when a file id disappears or expires.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")

    def upload_file_placeholder(self):
        """Document the observed upload endpoint without implementing upload."""
        # Expected endpoint:
        #   POST /files/upload
        #
        # Hypothesized HTTP method:
        #   POST
        #
        # Data to observe in Chrome DevTools Network:
        #   - request content type, likely multipart/form-data;
        #   - exact file field name used by the browser client;
        #   - optional fields for document type, signature mode or verification;
        #   - response schema, especially uploadedFiles[].id, type, signed, size;
        #   - validation errors for unsupported formats or files above limits;
        #   - whether anti-CSRF headers or session cookies are required.
        #
        # What is needed for SoluzioniOperative integration:
        #   - an authorized upload API or documented handoff mechanism;
        #   - a mapping from local document metadata to the upload payload;
        #   - rules for handling sensitive documents and upload auditability;
        #   - a non-production environment for tests.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")

    def get_certificates_placeholder(self):
        """Document the observed signer certificate lookup endpoint."""
        # Expected endpoint:
        #   GET /signature/fds/certificates/{signer_id}
        #
        # Hypothesized HTTP method:
        #   GET
        #
        # Data to observe in Chrome DevTools Network:
        #   - whether signer_id is a tax code, user id or account id;
        #   - certificate identifiers required by signing endpoints;
        #   - certificate labels, issuer, expiration and allowed uses;
        #   - whether the endpoint returns remote signature profiles;
        #   - session, authorization and tenant dependencies;
        #   - error behavior for unknown, expired or unauthorized signers.
        #
        # What is needed for SoluzioniOperative integration:
        #   - explicit authorization to use signer identifiers;
        #   - documented certificate selection rules;
        #   - privacy handling for personal identifiers;
        #   - a user consent and audit model for signature operations.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")

    def build_signature_image_placeholder(self):
        """Document the observed visible signature image builder endpoint."""
        # Expected endpoint:
        #   POST /signature/build-image
        #
        # Hypothesized HTTP method:
        #   POST
        #
        # Data to observe in Chrome DevTools Network:
        #   - payload fields for signer name, reason, location and date;
        #   - payload fields for page number and signature rectangle;
        #   - whether the response is an image, a binary blob or an image id;
        #   - whether the image id is referenced by the final PDF signing call;
        #   - whether invisible PDF signatures skip this endpoint.
        #
        # What is needed for SoluzioniOperative integration:
        #   - a documented model for visible PDF/PAdES signature placement;
        #   - UI rules for choosing page and coordinates;
        #   - a preview workflow that does not perform the legal signature;
        #   - consistency with ProtocolloMonitor document templates.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")

    def discover_pdf_signature_flow(self):
        """Document the missing PDF/PAdES signature flow."""
        # Expected endpoint:
        #   Unknown. Likely under /signature or /signature/pades.
        #
        # Hypothesized HTTP method:
        #   Unknown, likely POST for starting the signature transaction.
        #
        # Data to observe in Chrome DevTools Network:
        #   - request emitted after clicking Firma PDF;
        #   - uploaded file id passed to the request;
        #   - certificate id and signer id fields;
        #   - signature reason and visible/invisible signature options;
        #   - signature image id or placement fields, if visible signature is used;
        #   - transaction id returned before OTP;
        #   - relationship between start request, OTP request and final download.
        #
        # What is needed for SoluzioniOperative integration:
        #   - official endpoint and payload documentation;
        #   - explicit authorization for PAdES signing;
        #   - a reliable transaction state model;
        #   - audit logging requirements for legally relevant operations.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")

    def discover_cades_signature_flow(self):
        """Document the missing P7M/CAdES signature flow."""
        # Expected endpoint:
        #   Unknown. Likely under /signature or /signature/cades.
        #
        # Hypothesized HTTP method:
        #   Unknown, likely POST for starting the signature transaction.
        #
        # Data to observe in Chrome DevTools Network:
        #   - request emitted after clicking Firma P7M;
        #   - uploaded file id and original file type;
        #   - selected certificate id and signer id;
        #   - output format settings, such as .p7m envelope options;
        #   - transaction id returned before OTP;
        #   - status and download endpoint used after confirmation.
        #
        # What is needed for SoluzioniOperative integration:
        #   - documented CAdES parameters and output naming rules;
        #   - validation of accepted input formats;
        #   - storage policy for signed .p7m files;
        #   - user confirmation and audit model.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")

    def discover_xades_signature_flow(self):
        """Document the missing XML/XAdES signature flow."""
        # Expected endpoint:
        #   Unknown. Likely under /signature or /signature/xades.
        #
        # Hypothesized HTTP method:
        #   Unknown, likely POST for starting the signature transaction.
        #
        # Data to observe in Chrome DevTools Network:
        #   - request emitted after clicking Firma XML;
        #   - uploaded XML file id;
        #   - XAdES profile or policy fields;
        #   - namespace, transform or detached/enveloped signature options;
        #   - selected certificate id and signer id;
        #   - transaction id returned before OTP;
        #   - response and download behavior after confirmation.
        #
        # What is needed for SoluzioniOperative integration:
        #   - official XAdES profile supported by Trust Signer;
        #   - compatibility with XML documents produced or stored by the project;
        #   - validation strategy before and after signing;
        #   - agreement on preservation of XML metadata and namespaces.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")

    def discover_otp_flow(self):
        """Document the missing OTP request and confirmation flow."""
        # Expected endpoint:
        #   Unknown. Possible separate endpoints for OTP request and OTP confirm.
        #
        # Hypothesized HTTP method:
        #   Unknown, likely POST for both request and confirmation.
        #
        # Data to observe in Chrome DevTools Network:
        #   - endpoint called to request or send OTP;
        #   - transaction id created by the signature start endpoint;
        #   - fields that identify signer, certificate and signature operation;
        #   - endpoint called when the user enters OTP;
        #   - OTP confirmation response and resulting signed file id;
        #   - retry, expiration, cancellation and error codes;
        #   - whether OTP values ever appear in logs or payloads.
        #
        # What is needed for SoluzioniOperative integration:
        #   - a compliant user-driven OTP flow;
        #   - no storage of OTP values;
        #   - clear audit trail without sensitive secrets;
        #   - provider authorization for remote signing integration.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")

    def discover_download_flow(self):
        """Document the missing signed document download flow."""
        # Expected endpoint:
        #   Unknown. Possible endpoint under /files/download or /signature/download.
        #
        # Hypothesized HTTP method:
        #   Unknown, likely GET or POST depending on file id handling.
        #
        # Data to observe in Chrome DevTools Network:
        #   - request emitted when downloading the signed file;
        #   - whether download uses uploaded file id, signed file id or transaction id;
        #   - response content type and content disposition filename;
        #   - whether binary response is streamed or returned as encoded content;
        #   - expiration and authorization behavior;
        #   - differences between PDF, P7M and XML signed outputs.
        #
        # What is needed for SoluzioniOperative integration:
        #   - supported way to retrieve the signed artifact;
        #   - deterministic naming and storage in the document archive;
        #   - checksum or integrity verification;
        #   - error handling if the user cancels or download expires.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")

    def discover_verify_flow(self):
        """Document the missing signature verification flow."""
        # Expected endpoint:
        #   Unknown. Possible endpoint under /verification or /signature/verify.
        #
        # Hypothesized HTTP method:
        #   Unknown, likely POST for verification of an uploaded file.
        #
        # Data to observe in Chrome DevTools Network:
        #   - request emitted after clicking Verifica Firma;
        #   - whether verification reuses /files/upload or has a dedicated upload;
        #   - payload fields referencing file id or binary content;
        #   - response schema for signer, certificate, validity and timestamps;
        #   - validation status levels and error codes;
        #   - whether a report PDF or JSON report is available for download.
        #
        # What is needed for SoluzioniOperative integration:
        #   - official semantics for valid, warning and invalid states;
        #   - a mapping from verification report to ProtocolloMonitor metadata;
        #   - retention policy for verification evidence;
        #   - a user-facing review step for failed or uncertain verification.
        raise NotImplementedError("Discovery stub only; no HTTP call is allowed.")
