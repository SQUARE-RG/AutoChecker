int main() {
    try {
        throw "error";
    } catch (const char*) {
    }
    return 0;
}
