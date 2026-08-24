# Finding identity: rotation, canonical form, and cross-store matching

**Status: analysis only. Nothing here is built. It ends in numbered
questions for the director's ruling.**

Written for STEP-04 W4. It develops the one-paragraph sketch in STEP-02
§4d into a decision-ready proposal.

## 1. The problem, stated once

A finding's identity is derived from things that can change.

Today `content_hash` is a SHA-256 over the finding's evidence fields in
RFC 8785 canonical form. The `id` is the first 16 hex characters of that
hash. The attestation hash binds the confirming human to that content
hash. The chain head binds the ledger's length and last hash.

Three separate obligations turn out to be one problem:

| Obligation | The change | What breaks |
|---|---|---|
| OB-2 | Rotate the sealing key | Sealed refs are keyed under the sealing key (R-3). Refs sit inside the hashed content. So every `content_hash`, every `id`, every attestation and the head all change. |
| OB-3 (discharged) | Adopt a new canonical form | Canonical bytes change, so hashes change, so ids and attestations change. |
| OB-6 | Match findings across stores | Two stores with different keys produce different refs, so different hashes, so different ids for the same finding. |

One sentence: **anything that changes the bytes we hash, changes every
identity derived from them.**

A fourth hat, noted at the STEP-02 close: the canonical form and the
schema can change independently, and only the schema carries a version
number. There is no version axis for the canonical form.

## 2. Why this has not hurt yet

No store exists outside test fixtures. RFC 8785 was adopted while that was
still true, which cost nothing. The next change will not be free.

## 3. What a fix must preserve

Any proposal has to keep four things that are already ruled:

1. **Tamper-evidence.** A reader must still be able to detect that a
   record was altered after confirmation.
2. **The human gate.** Identity may never be re-assigned by a process that
   skips a person.
3. **No fabrication.** A migrated record may not claim to be something it
   was not.
4. **History stays readable.** Old records must remain verifiable, not
   just retained.

## 4. The options

### Option A: accept it, document it

Do nothing. Rotation means abandoning the old store; cross-store matching
never works.

- **Cost:** OB-2 stays permanently blocked. A key compromise means losing
  access to sealed evidence, which for a provenance tool is severe.
- **Verdict:** not viable as an end state, though it is the honest
  description of today.

### Option B: split the keys

Derive sealed refs from a **ref key** that is separate from the
**encryption key**. Rotation then re-encrypts blobs under a new encryption
key (MultiFernet) while the ref key, and therefore every hash and id,
stays fixed.

- **Solves:** OB-2 completely. Rotation becomes routine.
- **Does not solve:** OB-6. Two stores still have different ref keys, so
  ids still differ. And the ref key itself can never be rotated, which
  simply moves the frozen thing rather than removing it.
- **Cost:** one more secret to manage. A migration is still needed for
  existing stores, because today's refs are derived from the encryption
  key.

### Option C: content-derived identity, plus a keyed display ref

Hash the **plaintext digest** of the evidence rather than the store's
keyed ref. Concretely: the finding's hashed content carries an unkeyed
digest of the sealed plaintext, while the keyed ref stays a store-local
lookup handle and is excluded from hashing.

- **Solves:** OB-6 (identical findings get identical ids anywhere) and
  OB-2 (rotation does not touch the hashed bytes at all).
- **Reopens:** exactly the confirmation-oracle risk that R-3 closed. An
  unkeyed digest of the plaintext, present in an emitted artifact, lets
  anyone holding a candidate string test whether it is the sealed
  content, without unsealing and without an exposure log row.
- **Mitigation to evaluate:** keep the unkeyed digest **internal** to the
  hashed content and never emit it. But content_hash itself is emitted
  (SARIF fingerprints, FLARE evidence, packets), and content_hash is a
  hash of a structure containing that digest. That is one preimage step
  away from the same oracle for a guessable finding, since an attacker can
  construct the whole candidate record. This needs care, and it is the
  reason this option is not the recommendation despite solving the most.

### Option D: the supersession event (STEP-02 §4d, developed)

Treat every identity-changing event as a first-class, human-confirmed
ledger record, chained like any finding.

A supersession record commits to:

- the event type (`key-rotation`, `canonical-form-change`, `store-merge`),
- the old chain head and the new chain head,
- a map from old id to new id for every affected finding,
- the reason, and the human who confirmed it, with an attestation hash
  over all of the above.

Verification then walks the chain **through** supersession records instead
of stopping at them: history before the event stays verifiable under the
old rules, history after verifies under the new ones, and the join itself
is attested.

- **Solves:** OB-2 and canonical-form change as **instances of one
  mechanism** rather than two inventions. Preserves all four constraints
  in §3: the event is tamper-evident, human-confirmed, states plainly what
  changed rather than pretending nothing did, and keeps old records
  readable.
- **Does not solve:** OB-6 by itself. Cross-store matching still needs a
  shared basis for identity.
- **Cost:** verification becomes multi-epoch, which is real complexity in
  the one module that must stay simple enough to audit by eye.

### Option E: D plus a correlation digest for cross-store use

Option D for lifecycle events, plus an **optional** correlation value for
matching across stores when two parties both want it: an HMAC over the
plaintext digest under a **shared correlation key** exchanged out of band
between the two teams that intend to correlate.

- **Solves:** OB-6 for the case that actually matters, which is two teams
  who have agreed to compare notes, without creating a global oracle for
  everyone else. Anyone without the shared key learns nothing.
- **Cost:** key exchange is a human process, and this is a feature nobody
  has asked for yet.

## 5. Recommendation

**Adopt Option D now (when OB-2 is unblocked), and keep Option E on the
shelf for OB-6 until a real user needs cross-store matching.**

Reasons:

1. D is the only option that makes rotation and canonical-form change the
   *same* mechanism. That is worth more than solving either one alone,
   because the third instance of this problem class will then already have
   a home.
2. D preserves all four ruled constraints without weakening the R-3 oracle
   fix. C solves more on paper and pays for it in exactly the currency
   this project refuses to spend.
3. E is genuinely useful but speculative. Building it before a user asks
   would be inventing demand, which the charter's own evidence rules
   forbid.
4. B is a smaller change than D and worth considering as a first step
   *inside* D: if rotation is implemented via a supersession event anyway,
   splitting the keys reduces how many findings the event has to remap
   (possibly to zero). D and B are compatible; D and C are not.

## 6. What this would cost to build (rough shape, not a plan)

- A `supersession` record type in the canonical schema (major bump,
  migration note).
- `verify_chain` gaining epoch awareness: walk to a supersession record,
  verify its attestation, then continue under the new epoch's rules.
- A CLI command that performs a supersession, which is by construction a
  human-gated operation.
- Controls: a rotation that verifies clean across the join; a forged
  supersession record that fails; a supersession that claims a remap it
  did not perform, failing.

## 7. Honest limits of this paper

- No prototype was built, so all cost estimates are judgement, not
  measurement.
- Option C's oracle risk is argued, not demonstrated. If the director
  wants C reconsidered, the right next step is a concrete attack write-up,
  not a debate.
- The multi-epoch verification complexity in D is the part most likely to
  be underestimated here.
- None of this is urgent while no production store exists. The reason to
  decide now is that the decision is cheap now and expensive later, which
  is the same reason the RFC 8785 adoption happened when it did.

## 8. Numbered questions for ruling

1. **Adopt Option D as the identity-lifecycle mechanism?** Yes, or name
   another option to develop instead.
2. **If D: does OB-2 (key rotation) unblock now**, to be implemented in a
   later phase under its own contract, or does it stay blocked until a
   supersession prototype exists?
3. **Is Option B (split ref key from encryption key) adopted as part of
   D**, to shrink or eliminate the remap? It is a small change with one
   more secret to manage.
4. **Is Option E (shared-key correlation digest) parked as a named future
   feature for OB-6**, or ruled out entirely so nobody proposes it again?
5. **Does the canonical form get its own version number** (the fourth hat),
   separate from the schema version, so a future form change has an axis
   to announce itself on?
6. **Should Option C be reconsidered** on the strength of a written attack
   analysis, or is the R-3 oracle fix treated as settled and C closed?
