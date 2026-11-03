int main() {
    int retries = 2;
    bool failed = false;
    if (!failed && retries > 0) {
        retries--;
    }
    return retries;
}
