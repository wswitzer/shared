# Visita Segura — brokerage-validation prototype

Spanish-first interactive prototype for a Guadalajara real-estate safe-showing coordination layer. All names, addresses, people and metrics are fictional demo data.

## Open

- `index.html` — Spanish (default)
- `en.html` — English

The left navigation uses real hash links, so the major screens still switch even in environments that restrict JavaScript. JavaScript only enhances the agent-state actions and small UI interactions. The dashboard and timeline demo data are pre-rendered so they are visible without JavaScript.

## Main demo path

1. Monitoring dashboard
2. Open an overdue showing and review its timeline
3. Agent view → Start showing
4. I’m OK / Extend / Finish / I need help
5. Brokerage protocol settings
6. Compliance analytics
7. Integration concept

## Product boundaries shown in the prototype

- Brokerage owns its protocol and escalation decisions.
- The product does not provide or guarantee emergency response.
- Location is framed as temporary during a showing.
- No government-ID images are needed for the demo.
- Analytics focus on whether the brokerage follows its own protocol, not agent gamification.

## Validation assumptions

The key questions remain whether brokerages have enough execution/follow-up pain to pay, who owns monitoring today, how much double-entry agents tolerate, whether live location is acceptable, what WhatsApp integration is necessary, and whether an owner will actually commit to a MX$3,000 / 14-day pilot.
