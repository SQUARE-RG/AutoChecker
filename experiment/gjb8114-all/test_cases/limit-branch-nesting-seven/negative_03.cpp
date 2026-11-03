void nested_switches(int v) {
    switch (v) {
        case 1:
            switch (v) {
                case 1:
                    switch (v) {
                        case 1:
                            switch (v) {
                                case 1:
                                    switch (v) {
                                        case 1:
                                            switch (v) {
                                                case 1:
                                                    switch (v) {
                                                        case 1:
                                                            switch (v) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-4-1]
                                                                case 1:
                                                                    break;
                                                                default:
                                                                    break;
                                                            }
                                                            break;
                                                        default:
                                                            break;
                                                    }
                                                    break;
                                                default:
                                                    break;
                                            }
                                            break;
                                        default:
                                            break;
                                    }
                                    break;
                                default:
                                    break;
                            }
                            break;
                        default:
                            break;
                    }
                    break;
                default:
                    break;
            }
            break;
        default:
            break;
    }
}
