import https from 'https';

// Replace with your Mastodon server domain
const server = 'streaming.mastodon.social';

console.log('Checking if the streaming service is alive...');

https.get(`https://${server}/api/v1/streaming/health`, (res) => {
  console.log('Status Code:', res.statusCode);

  res.on('data', (d) => {
    process.stdout.write(d);
  });

  res.on('end', () => {
    console.log('\nStreaming service check complete.');
  });
}).on('error', (e) => {
  console.error('Error:', e);
});
