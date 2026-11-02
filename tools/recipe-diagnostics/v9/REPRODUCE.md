The complete reviewed Java source is `../RecipeExceptionObserver.java`. These commands compile it for Java17 and rerun its isolated child-process fixture; they do not start or attach to Minecraft:

```text
<javac17-or-newer> --release 17 --add-modules jdk.jdi -d <private-artifacts>/classes ../RecipeExceptionObserver.java
<full-jdk17-java> --add-modules jdk.jdi -cp <private-artifacts>/classes RecipeExceptionObserver --self-test <new-empty-private-artifacts-directory> <full-jdk17-java>
```

Run from this source folder with explicit compiler/runtime paths. The fixture creates only its own synthetic debuggee and files. Published JAR bytes remain separately SHA-pinned; compiler/ZIP metadata can change a local rebuilt JAR hash. `validation.json` and the native profile distinguish modeled observations, exact static native bindings and the existing launcher429 archive fixture from real-player delivery.
