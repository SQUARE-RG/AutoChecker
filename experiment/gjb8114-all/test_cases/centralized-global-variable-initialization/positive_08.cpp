struct ServiceConfig {
    static int timeoutSeconds;
};

int ServiceConfig::timeoutSeconds;

void InitializeGlobals() {
    ServiceConfig::timeoutSeconds = 30;
}

int main() {
    InitializeGlobals();
    return ServiceConfig::timeoutSeconds == 30 ? 0 : 1;
}
