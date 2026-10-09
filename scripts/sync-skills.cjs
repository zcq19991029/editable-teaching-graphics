// Publish a fixed file allowlist; do not copy credentials or task assets.
const fs=require('fs'),path=require('path');
const source=process.argv[2];
if(!source)throw Error('Usage: node scripts/sync-skills.cjs <source-skills-directory>');
const from=fs.realpathSync(source),root=path.resolve(__dirname,'..');
const names=['teach-1-plan','teach-2-gen','teach-3-embed','teach-4-ppt'];
const files=names.flatMap(n=>[`${n}/SKILL.md`,`${n}/agents/openai.yaml`]);
files.push('teach-2-gen/references/image-spec.md');
files.push('teach-1-plan/references/input-ocr.md');
const inputs=files.map(rel=>{
 const p=path.join(from,rel);if(!fs.statSync(p).isFile())throw Error('Missing source file: '+rel);
 return {rel,content:fs.readFileSync(p)};
});
for(const {rel,content} of inputs){
 const dest=path.join(root,'.agents/skills',rel);
 fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,content);
}
console.log(JSON.stringify({skills:names,files:inputs.length,sourceModified:false},null,2));
