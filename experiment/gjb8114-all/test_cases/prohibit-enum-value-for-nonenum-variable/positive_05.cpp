enum Status { ok = 1, fail = 2 };

void consume(Status code) {
    (void)code;
}

int main() {
    consume(ok);
    return 0;
}
