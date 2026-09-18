const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason
} = require('@whiskeysockets/baileys');
const pino = require('pino');

const phoneNumber = process.argv[2] || '19514455799';
const sessionDir = '/data/whatsapp/session';

async function generatePairingCode() {
  const { state, saveCreds } = await useMultiFileAuthState(sessionDir);
  
  const sock = makeWASocket({
    auth: state,
    logger: pino({ level: 'silent' }),
    printQRInTerminal: false,
    browser: ['Chrome (Linux)', '', '']
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect } = update;
    
    if (connection === 'open') {
      console.log('WHATSAPP_CONNECTED_SUCCESSFULLY');
      process.exit(0);
    }
    
    if (connection === 'close') {
      const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
      if (shouldReconnect) {
        generatePairingCode();
      }
    }
  });

  // Request 8-digit pairing code
  setTimeout(async () => {
    try {
      const code = await sock.requestPairingCode(phoneNumber);
      console.log('PAIRING_CODE:' + code);
    } catch (err) {
      console.error('Error requesting pairing code:', err);
    }
  }, 3000);
}

generatePairingCode();
