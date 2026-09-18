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
  });

  // Wait for socket to be ready, then request code
  setTimeout(async () => {
    try {
      const code = await sock.requestPairingCode(phoneNumber);
      console.log('\n=== PAIRING CODE ===\n' + code + '\n====================\n');
    } catch (err) {
      console.error('Error:', err.message);
    }
  }, 4000);
}

generatePairingCode();
