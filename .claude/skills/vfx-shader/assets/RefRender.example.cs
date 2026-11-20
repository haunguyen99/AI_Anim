using VfxKit; using UnityEngine; using UnityEditor; using System.Text; using System.IO; using System.Linq;
namespace VfxEffects {
public static class RefRender {
  static string G(ParticleSystem.MinMaxGradient g){ string s=g.mode.ToString()+":"; switch(g.mode){ case ParticleSystemGradientMode.Color: return s+ColorUtility.ToHtmlStringRGBA(g.color); case ParticleSystemGradientMode.TwoColors: return s+ColorUtility.ToHtmlStringRGBA(g.colorMin)+".."+ColorUtility.ToHtmlStringRGBA(g.colorMax); default: { var gr=g.gradientMax; if(gr!=null){ foreach(var k in gr.colorKeys) s+="c("+k.time.ToString("0.##")+" "+ColorUtility.ToHtmlStringRGB(k.color)+")"; foreach(var k in gr.alphaKeys) s+="a("+k.time.ToString("0.##")+" "+k.alpha.ToString("0.##")+")"; } return s; } } }
  static string C(ParticleSystem.MinMaxCurve c){ switch(c.mode){case ParticleSystemCurveMode.Constant:return c.constant.ToString("0.###");case ParticleSystemCurveMode.TwoConstants:return c.constantMin.ToString("0.###")+".."+c.constantMax.ToString("0.###");default:{var k=c.curve; string s="curve*"+c.curveMultiplier.ToString("0.###")+"["; if(k!=null) foreach(var key in k.keys) s+="("+key.time.ToString("0.##")+","+key.value.ToString("0.##")+")"; return s+"]"+(c.mode==ParticleSystemCurveMode.TwoCurves?" (two)":"");}} }
  public static void Run(){
    var path=System.Environment.GetEnvironmentVariable("REF_PREFAB");
    var outp=System.Environment.GetEnvironmentVariable("REF_OUT");
    var times=System.Environment.GetEnvironmentVariable("REF_TIMES").Split(',').Select(float.Parse).ToArray();
    var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path);
    var sb=new StringBuilder();
    sb.AppendLine("PREFAB "+path+" rootScale "+prefab.transform.localScale);
    foreach(var ps in prefab.GetComponentsInChildren<ParticleSystem>(true)){
      var t=ps.transform; string full=t.name; var p=t.parent; while(p){full=p.name+"/"+full;p=p.parent;}
      var m=ps.main; var r=ps.GetComponent<ParticleSystemRenderer>();
      sb.AppendLine("== "+full+"  active="+t.gameObject.activeSelf+" pos="+t.localPosition+" rot="+t.localEulerAngles+" scale="+t.localScale);
      sb.AppendLine(" main: dur="+m.duration+" loop="+m.loop+" delay="+C(m.startDelay)+" life="+C(m.startLifetime)+" speed="+C(m.startSpeed)+" size="+(m.startSize3D?"3D("+C(m.startSizeX)+","+C(m.startSizeY)+","+C(m.startSizeZ)+")":C(m.startSize))+" rotRad="+(m.startRotation3D?"3D("+C(m.startRotationX)+","+C(m.startRotationY)+","+C(m.startRotationZ)+")":C(m.startRotation))+" prewarm="+m.prewarm+" playOnAwake="+m.playOnAwake+" speedMul="+m.simulationSpeed+" color="+G(m.startColor)+" space="+m.simulationSpace+" scaling="+m.scalingMode+" max="+m.maxParticles+" grav="+C(m.gravityModifier));
      var e=ps.emission; sb.Append(" emission: rate="+C(e.rateOverTime)+" bursts="+e.burstCount); for(int i=0;i<e.burstCount;i++){var b=e.GetBurst(i); sb.Append(" [t"+b.time+" n"+C(b.count)+"]");} sb.AppendLine();
      var s=ps.shape; if(s.enabled) sb.AppendLine(" shape: "+s.shapeType+" r="+s.radius+" thick="+s.radiusThickness+" angle="+s.angle+" arc="+s.arc+" pos="+s.position+" rot="+s.rotation+" scale="+s.scale);
      var v=ps.velocityOverLifetime; if(v.enabled) sb.AppendLine(" VEL: lin("+C(v.x)+","+C(v.y)+","+C(v.z)+") orb("+C(v.orbitalX)+","+C(v.orbitalY)+","+C(v.orbitalZ)+") radial="+C(v.radial)+" speedMod="+C(v.speedModifier)+" space="+v.space);
      var f=ps.forceOverLifetime; if(f.enabled) sb.AppendLine(" FORCE: "+C(f.x)+","+C(f.y)+","+C(f.z));
      var ro=ps.rotationOverLifetime; if(ro.enabled) sb.AppendLine(" ROT: sep="+ro.separateAxes+" "+(ro.separateAxes?C(ro.x)+","+C(ro.y)+","+C(ro.z):C(ro.z)));
      var sz=ps.sizeOverLifetime; if(sz.enabled) sb.AppendLine(" SIZE: sep="+sz.separateAxes+" "+(sz.separateAxes?C(sz.x)+" | "+C(sz.y)+" | "+C(sz.z):C(sz.size)));
      var co=ps.colorOverLifetime; if(co.enabled){ sb.Append(" COLOR: "); var g=co.color.gradient; if(g!=null){foreach(var k in g.colorKeys) sb.Append("c("+k.time.ToString("0.##")+" "+ColorUtility.ToHtmlStringRGB(k.color)+")"); foreach(var k in g.alphaKeys) sb.Append("a("+k.time.ToString("0.##")+" "+k.alpha.ToString("0.##")+")");} sb.AppendLine(); }
      var nz=ps.noise; if(nz.enabled) sb.AppendLine(" NOISE: str="+C(nz.strength)+" freq="+nz.frequency+" scroll="+C(nz.scrollSpeed));
      var cd=ps.customData; if(cd.enabled){ for(int st=0;st<2;st++){var cs=(ParticleSystemCustomData)st; var mode=cd.GetMode(cs); sb.Append(" CUSTOM"+(st+1)+": "+mode); if(mode==ParticleSystemCustomDataMode.Color) sb.Append(" "+G(cd.GetColor(cs))); if(mode==ParticleSystemCustomDataMode.Vector){ for(int i=0;i<cd.GetVectorComponentCount(cs);i++) sb.Append(" ["+i+"]="+C(cd.GetVector(cs,i))); } sb.AppendLine(); } }
      var ts=ps.textureSheetAnimation; if(ts.enabled) sb.AppendLine(" TSA: "+ts.numTilesX+"x"+ts.numTilesY+" mode="+ts.mode+" anim="+ts.animation+" frame="+C(ts.frameOverTime)+" start="+C(ts.startFrame)+" cycles="+ts.cycleCount+" row="+ts.rowIndex+" uvChannel="+ts.uvChannelMask);
      if(ts.enabled&&ts.mode==ParticleSystemAnimationMode.Sprites){ sb.Append(" SPRITES("+ts.spriteCount+"):"); for(int i=0;i<ts.spriteCount;i++){ var sp=ts.GetSprite(i); sb.Append(" "+(sp?sp.name+"@"+(sp.texture?sp.texture.name:"?")+"["+sp.rect.width+"x"+sp.rect.height+"]":"null")); } sb.AppendLine(); }
      var sub=ps.subEmitters; if(sub.enabled) sb.AppendLine(" SUB: "+sub.subEmittersCount);
      string mats=string.Join(", ",r.sharedMaterials.Select(x=>x? x.name+" ["+x.shader.name+"]":"null"));
      var st_=new System.Collections.Generic.List<ParticleSystemVertexStream>(); r.GetActiveVertexStreams(st_); sb.AppendLine(" streams: "+string.Join(",",st_)+"  shadows="+r.shadowCastingMode+" minmaxSize="+r.minParticleSize+"/"+r.maxParticleSize+" flip="+r.flip+" sortFudge="+r.sortingFudge+" sortMode="+r.sortMode+" maskInt="+r.maskInteraction);
      sb.AppendLine(" render: mode="+r.renderMode+" align="+r.alignment+" mesh="+(r.mesh?r.mesh.name:"-")+" sort="+r.sortingOrder+" mats="+mats+" len="+r.lengthScale+" vel="+r.velocityScale+" pivot="+r.pivot);
      foreach(var mm in r.sharedMaterials) if(mm){ sb.Append("   MAT "+mm.name+" queue="+mm.renderQueue+" mainTex="+(mm.mainTexture?mm.mainTexture.name:"null")+" kw="+string.Join("|",mm.shaderKeywords)+" : "); var sh=mm.shader; for(int i=0;i<ShaderUtil.GetPropertyCount(sh);i++){ var n=ShaderUtil.GetPropertyName(sh,i); var ty=ShaderUtil.GetPropertyType(sh,i); if(ty==ShaderUtil.ShaderPropertyType.TexEnv){ var tx=mm.GetTexture(n); if(tx) sb.Append(n+"="+tx.name+"(x"+mm.GetTextureScale(n)+") "); } else if(ty==ShaderUtil.ShaderPropertyType.Color) sb.Append(n+"="+mm.GetColor(n)+" "); else if(ty==ShaderUtil.ShaderPropertyType.Float||ty==ShaderUtil.ShaderPropertyType.Range) sb.Append(n+"="+mm.GetFloat(n).ToString("0.###")+" "); else if(ty==ShaderUtil.ShaderPropertyType.Vector) sb.Append(n+"="+mm.GetVector(n)+" "); } sb.AppendLine(); }
    }
    File.WriteAllText(outp+".txt",sb.ToString());
    int size=int.Parse(System.Environment.GetEnvironmentVariable("REF_SIZE")??"384");
    var cp=System.Environment.GetEnvironmentVariable("REF_CAM").Split(',').Select(float.Parse).ToArray();
    VfxBuildKit.CaptureSheet(prefab,times,outp+".png",size,new Vector3(cp[0],cp[1],cp[2]),new Vector3(cp[3],cp[4],cp[5]));
  }
}}
