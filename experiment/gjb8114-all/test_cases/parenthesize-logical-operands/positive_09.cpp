int main() {
    unsigned int flags = 0x21;
    unsigned int threshold = 0x40;
    bool result = false;
    if ((flags << 1) > threshold)
    {
        result = true;
    }
    return result ? 0 : 1;
}
