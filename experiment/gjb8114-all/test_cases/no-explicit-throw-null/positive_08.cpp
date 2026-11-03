int check(bool ok) {
    if (!ok) {
        throw "failure";
    }
    return 0;
}

int main() {
    try {
        return check(true);
    } catch (const char*) {
        return 1;
    }
}
