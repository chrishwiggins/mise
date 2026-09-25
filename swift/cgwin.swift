import CoreGraphics
import Foundation
let ids: Set<Int> = [387, 96692, 182888, 217570]
let list = CGWindowListCopyWindowInfo([.optionAll], kCGNullWindowID) as! [[String: Any]]
for w in list {
    let n = w["kCGWindowNumber"] as! Int
    if ids.contains(n) {
        print(n, w["kCGWindowOwnerName"] ?? "", "layer=\(w["kCGWindowLayer"] ?? "")", "alpha=\(w["kCGWindowAlpha"] ?? "")", "onscreen=\(w["kCGWindowIsOnscreen"] ?? false)", "bounds=\(w["kCGWindowBounds"] ?? "")", "name=\(w["kCGWindowName"] ?? "")")
    }
}
