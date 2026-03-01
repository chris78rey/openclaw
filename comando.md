# Comandos para validar el stack en el VPS

Usa estos bloques tal cual.

## 1. Entrar al directorio del proyecto

```bash
cd /ruta/al/proyecto
```

## 2. Dar permisos al script

```bash
chmod +x scripts/validate_vps_stack.sh
```

## 3. Ejecutar validacion completa contra el dominio publico

```bash
./scripts/validate_vps_stack.sh bot.da-tica.com
```

## 4. Si quieres usar otro dominio

```bash
./scripts/validate_vps_stack.sh TU-DOMINIO.COM
```

## 5. Commit y push de este cambio en la rama actual

```bash
git add scripts/validate_vps_stack.sh comando.md
git commit -m "chore(ops): add vps validation script"
git push origin web_sin_telegram
```
