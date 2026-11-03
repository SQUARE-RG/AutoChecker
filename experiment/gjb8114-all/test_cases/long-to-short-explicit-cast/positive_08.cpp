int main() {
    unsigned long wideValue = 300UL;
    unsigned char narrowValue = 0;
    narrowValue = static_cast<unsigned char>(wideValue);
    return static_cast<int>(narrowValue);
}
