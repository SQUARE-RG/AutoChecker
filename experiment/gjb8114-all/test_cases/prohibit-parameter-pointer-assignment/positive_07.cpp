int read_if_valid(int* p, int fallback)
{
    if (p != nullptr) {
        return *p;
    }
    return fallback;
}
