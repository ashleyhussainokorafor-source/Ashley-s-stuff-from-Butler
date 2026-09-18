const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason
} = require('@whiskeysockets/baileys');
const pino = require('pino');

const phoneNumber = '19514455799';
const sessionDir = '/data/whatsapp/session';

async function startPairing() {
  const { state, saveCreds } = await useMultiFileAuthState(sessionDir);
  
  const sock = makeWASocket({
    auth: state,
    logger: pino({ level: 'silent' }),
    printQRInTerminal: false,
    browser: ['Ubuntu', 'Chrome', '22.04']
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect } = update;
    if (connection === 'open') {
      console.log('SUCCESS: WhatsApp is paired and connected!');
    }
  });

  setTimeout(async () => {
    try {
      const code = await sock.requestPairingCode(phoneNumber);
      console.log('PAIRING_CODE_IS:' + code);
    } catch (err) {
      console.log('CODE_ERROR:' + err.message);
    }
  }, 3500);

  // Keep alive for 120 seconds waiting for user to type the code
  await new Promise(resolve => setTimeout(resolve, 120000));
}

startPairing();
