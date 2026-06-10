//
//  H1mekaRTXProbeInstaller_H1mekaRTXProbeInstallerUITestsLaunchTests.swift
//  H1mekaRTXProbeInstaller H1mekaRTXProbeInstallerUITests
//
//  Created by 히메카 on 6/11/26.
//

import XCTest

final class H1mekaRTXProbeInstaller_H1mekaRTXProbeInstallerUITestsLaunchTests: XCTestCase {

    override class var runsForEachTargetApplicationUIConfiguration: Bool {
        true
    }

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    @MainActor
    func testLaunch() throws {
        let app = XCUIApplication()
        app.launch()

        // Insert steps here to perform after app launch but before taking a screenshot,
        // such as logging into a test account or navigating somewhere in the app

        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = "Launch Screen"
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
