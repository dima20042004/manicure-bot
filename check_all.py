print("Проверка установленных библиотек...")
print("=" * 40)

libs = [
    "regex",
    "importlib_metadata",
    "tokenizers", 
    "typer",
    "accelerate",
    "safetensors",
    "diffusers",
    "transformers",
    "torch"
]

for lib in libs:
    try:
        __import__(lib)
        print(f"✅ {lib} - УСТАНОВЛЕН")
    except ImportError:
        print(f"❌ {lib} - НЕ УСТАНОВЛЕН")

print("=" * 40)
input("Нажмите Enter для выхода...")