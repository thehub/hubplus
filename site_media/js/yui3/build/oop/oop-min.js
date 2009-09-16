YUI.add("oop",function(E){var D=E.Lang,C=E.Array,B=Object.prototype;E.augment=function(A,S,H,Q,M){var K=S.prototype,O=null,R=S,N=(M)?E.Array(M):[],G=A.prototype,L=G||A,P=false,F,I,J;if(G&&R){F={};I={};O={};E.each(K,function(U,T){I[T]=function(){for(J in F){if(F.hasOwnProperty(J)&&(this[J]===I[J])){this[J]=F[J];}}R.apply(this,N);return F[T].apply(this,arguments);};if((!Q||(T in Q))&&(H||!(T in this))){if(D.isFunction(U)){F[T]=U;this[T]=I[T];}else{this[T]=U;}}},O,true);}else{P=true;}E.mix(L,O||K,H,Q);if(P){S.apply(L,N);}return A;};E.aggregate=function(G,F,A,H){return E.mix(G,F,A,H,0,true);};E.extend=function(H,G,A,J){if(!G||!H){E.error("extend failed, verify dependencies");}var I=G.prototype,F=E.Object(I);H.prototype=F;F.constructor=H;H.superclass=I;if(G!=Object&&I.constructor==B.constructor){I.constructor=G;}if(A){E.mix(F,A,true);}if(J){E.mix(H,J,true);}return H;};E.each=function(G,F,H,A){if(G.each&&G.item){return G.each.call(G,F,H);}else{switch(C.test(G)){case 1:return C.each(G,F,H);case 2:return C.each(E.Array(G,0,true),F,H);default:return E.Object.each(G,F,H,A);}}};E.clone=function(I,H,G,J,A){if(!D.isObject(I)){return I;}var F;switch(D.type(I)){case"date":return new Date(I);case"regexp":return new RegExp(I.source);case"function":F=E.bind(I,A);break;case"array":F=[];break;default:F=(H)?{}:E.Object(I);}E.each(I,function(L,K){if(!G||(G.call(J||this,L,K,this,I)!==false)){this[K]=E.clone(L,H,G,J,A||I);}},F);return F;};E.bind=function(A,G){var F=arguments.length>2?E.Array(arguments,2,true):null;return function(){var I=D.isString(A)?G[A]:A,H=(F)?F.concat(E.Array(arguments,0,true)):arguments;return I.apply(G||I,H);};};E.rbind=function(A,G){var F=arguments.length>2?E.Array(arguments,2,true):null;return function(){var I=D.isString(A)?G[A]:A,H=(F)?E.Array(arguments,0,true).concat(F):arguments;return I.apply(G||I,H);};};},"@VERSION@");