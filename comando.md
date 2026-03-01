# Comandos para actualizar y ejecutar la version nueva del script

Usa estos bloques tal cual.

## 1. Entrar al repo existente

```bash
cd ~/openclaw
```

## 2. Actualizar referencias de la rama remota

```bash
git fetch origin web_sin_telegram
```

## 3. Traer la version nueva del script

```bash
git checkout origin/web_sin_telegram -- scripts/validate_vps_stack.sh
```

## 4. Dar permisos de ejecucion

```bash
chmod +x scripts/validate_vps_stack.sh
```

## 5. Ejecutar la validacion con timeout por defecto

```bash
./scripts/validate_vps_stack.sh bot.da-tica.com
```

## 6. Ejecutar la validacion con mas margen si hace falta

```bash
CHECK_TIMEOUT=20 ./scripts/validate_vps_stack.sh bot.da-tica.com
```
