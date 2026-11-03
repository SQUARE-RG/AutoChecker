namespace {
template <typename T>
T identity(T v) {
    return v;
}

template <>
const char* identity<const char*>(const char* v) { return v; }
}

int main() {
    int n = identity(7);
    const char* p = identity("text");
    return (n == 7 && p[0] == 't') ? 0 : 1;
}
