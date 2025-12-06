// Wordle Solver Content Script
// Automatically reads Wordle game state and displays suggestions

(function () {
  "use strict";

  const API_URL = "http://localhost:5000/api";
  const DEBUG = true; // Enable debug mode to troubleshoot
  const MESSAGE_PREFIX = "WORDLE_SOLVER_";
  let suggestionsPanel = null;
  let currentGuesses = [];
  let currentFeedback = [];
  const isInIframe = window.self !== window.top;

  // Create suggestions panel
  function createSuggestionsPanel() {
    if (suggestionsPanel) {
      if (DEBUG) console.log("Wordle Solver: Panel already exists");
      return;
    }

    try {
      if (DEBUG) console.log("Wordle Solver: Creating panel...");

      // Wait for body to be available
      if (!document.body) {
        if (DEBUG) console.log("Wordle Solver: Body not ready, waiting...");
        setTimeout(createSuggestionsPanel, 100);
        return;
      }

      // Always create panel - it will be shown on the main page
      // If we're in an iframe, we'll send messages to the main page

      suggestionsPanel = document.createElement("div");
      suggestionsPanel.id = "wordle-solver-panel";
      suggestionsPanel.innerHTML = `
            <div class="solver-header">
                <h3>🤖 Wordle Solver</h3>
                <div>
                    <button id="solver-refresh" style="margin-right: 5px;">Refresh</button>
                    <button id="solver-toggle">Hide</button>
                </div>
            </div>
            <div class="solver-content">
                <div style="margin-bottom: 8px; padding: 5px; background: #f0f0f0; border-radius: 4px;">
                    <label style="display: flex; align-items: center; cursor: pointer; font-size: 12px;">
                        <input type="checkbox" id="solver-use-ml" style="margin-right: 5px;">
                        <span>Use ML Model (requires --model flag when starting server)</span>
                    </label>
                </div>
                <div id="solver-status">Reading game state...</div>
                <div id="solver-suggestions"></div>
                <div id="solver-starting-words" style="display:none;">
                    <strong>Best Starting Words:</strong>
                    <div id="starting-words-list"></div>
                </div>
            </div>
        `;

      document.body.appendChild(suggestionsPanel);

      // Ensure panel is visible
      if (suggestionsPanel) {
        suggestionsPanel.style.display = "block";
        if (DEBUG)
          console.log("Wordle Solver: Panel added to DOM and made visible");
      } else {
        if (DEBUG) console.error("Wordle Solver: Failed to create panel!");
      }

      // Toggle button
      const toggleBtn = document.getElementById("solver-toggle");
      if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
          const content = suggestionsPanel.querySelector(".solver-content");
          const isHidden = content.style.display === "none";
          content.style.display = isHidden ? "block" : "none";
          document.getElementById("solver-toggle").textContent = isHidden
            ? "Hide"
            : "Show";
        });
      }

      // Refresh button
      const refreshBtn = document.getElementById("solver-refresh");
      if (refreshBtn) {
        refreshBtn.addEventListener("click", () => {
          if (DEBUG) console.log("Wordle Solver: Manual refresh triggered");
          currentGuesses = []; // Reset to force update
          currentFeedback = [];
          updateSuggestions();
        });
      }

      // ML toggle checkbox
      const mlToggle = document.getElementById("solver-use-ml");
      if (mlToggle) {
        // Load saved preference
        const savedUseML = localStorage.getItem("wordleSolverUseML") === "true";
        mlToggle.checked = savedUseML;

        // Update preference when toggled
        mlToggle.addEventListener("change", (e) => {
          const useML = e.target.checked;
          localStorage.setItem("wordleSolverUseML", useML.toString());
          if (DEBUG) console.log("Wordle Solver: ML toggle changed to", useML);
          // Refresh suggestions with new setting
          currentGuesses = []; // Reset to force update
          currentFeedback = [];
          updateSuggestions();
        });
      }

      if (DEBUG) console.log("Wordle Solver: Panel created successfully");
    } catch (error) {
      console.error("Wordle Solver: Error creating panel:", error);
    }
  }

  // Diagnostic function to find Wordle game structure
  function diagnoseWordleStructure() {
    console.log("=== Wordle Structure Diagnosis ===");
    console.log("URL:", window.location.href);
    console.log("In iframe:", window.self !== window.top);

    // Check for common Wordle elements
    const checks = {
      "game-app": document.querySelectorAll("game-app").length,
      "game-row": document.querySelectorAll("game-row").length,
      "game-tile": document.querySelectorAll("game-tile").length,
      "game-board": document.querySelectorAll("game-board").length,
      "[data-testid='tile']": document.querySelectorAll("[data-testid='tile']")
        .length,
      "[class*='Tile']": document.querySelectorAll("[class*='Tile']").length,
      "[role='img'][aria-roledescription='tile']": document.querySelectorAll(
        "[role='img'][aria-roledescription='tile']"
      ).length,
      "[id*='wordle']": document.querySelectorAll("[id*='wordle']").length,
      "[class*='wordle']":
        document.querySelectorAll("[class*='wordle']").length,
      "[class*='game']": document.querySelectorAll("[class*='game']").length,
      ".tile[data-state]":
        document.querySelectorAll(".tile[data-state]").length,
    };

    console.log("Element counts:", checks);

    // Check tile structure (supports both NYTimes and Wordle Unlimited)
    const tiles = document.querySelectorAll(
      '[data-testid="tile"], [class*="Tile-module"], [role="img"][aria-roledescription="tile"], .tile[data-state]'
    );
    if (tiles.length > 0) {
      console.log(`Found ${tiles.length} tile elements`);
      const firstTile = tiles[0];
      console.log("First tile:", firstTile);
      console.log(
        "First tile aria-label:",
        firstTile.getAttribute("aria-label")
      );
      console.log(
        "First tile data-state:",
        firstTile.getAttribute("data-state")
      );
      console.log("First tile classes:", firstTile.className);
    }

    // Try to find game-row elements and their structure
    const rows = document.querySelectorAll("game-row");
    if (rows.length > 0) {
      console.log(`Found ${rows.length} game-row elements`);
      const firstRow = rows[0];
      console.log("First row:", firstRow);
      console.log(
        "First row shadow root:",
        firstRow.shadowRoot ? "exists" : "none"
      );

      if (firstRow.shadowRoot) {
        const tiles = firstRow.shadowRoot.querySelectorAll("game-tile");
        console.log(`First row has ${tiles.length} tiles in shadow DOM`);
        if (tiles.length > 0) {
          const firstTile = tiles[0];
          console.log("First tile:", firstTile);
          console.log(
            "First tile letter attr:",
            firstTile.getAttribute("letter")
          );
          console.log(
            "First tile evaluation attr:",
            firstTile.getAttribute("evaluation")
          );
        }
      }
    }

    // Check parent elements
    if (rows.length > 0) {
      const parent = rows[0].parentElement;
      console.log(
        "Parent of game-row:",
        parent?.tagName,
        parent?.id,
        parent?.className
      );
    }

    console.log("=== End Diagnosis ===");
  }

  // Expose diagnostic function globally for manual testing
  window.wordleSolverDiagnose = diagnoseWordleStructure;

  // Debug function to inspect tile parsing
  window.wordleSolverDebugTiles = function () {
    console.log("=== Wordle Solver: Tile Debug ===");
    const tiles = document.querySelectorAll(
      '[data-testid="tile"], [class*="Tile-module"], [role="img"][aria-roledescription="tile"], .tile[data-state]'
    );
    console.log(`Found ${tiles.length} tiles`);

    const tileInfo = [];
    tiles.forEach((tile, index) => {
      const ariaLabel = tile.getAttribute("aria-label") || "";
      const dataState = tile.getAttribute("data-state") || "";
      const textContent = tile.textContent?.trim() || "";

      // Try to extract letter using the same logic as the parser
      // FIRST: Check textContent (most reliable - letter is directly in DOM)
      let letter = "";
      if (
        textContent &&
        textContent.length === 1 &&
        /[a-z]/i.test(textContent)
      ) {
        letter = textContent.toLowerCase();
      } else {
        // FALLBACK: Parse from aria-label
        let match = ariaLabel.match(/letter,\s*([A-Z])\s*,/i);
        if (match) {
          letter = match[1].toLowerCase();
        } else {
          match = ariaLabel.match(/,\s*([A-Z])\s*,/i);
          if (match) {
            letter = match[1].toLowerCase();
          } else {
            match = ariaLabel.match(/letter,\s*([A-Z])\s+/i);
            if (match) {
              letter = match[1].toLowerCase();
            } else {
              match = ariaLabel.match(/,\s*([A-Z])\s+/i);
              if (match) {
                letter = match[1].toLowerCase();
              } else {
                match = ariaLabel.match(/\b([A-Z])\b/);
                if (match) {
                  letter = match[1].toLowerCase();
                }
              }
            }
          }
        }
      }

      tileInfo.push({
        index,
        ariaLabel,
        extractedLetter: letter || "(none)",
        dataState,
        textContent,
        position: ariaLabel.match(/(\d+)(?:st|nd|rd|th)/i)?.[1] || "unknown",
      });
    });

    console.table(tileInfo);

    // Group into rows
    const rows = [];
    for (let i = 0; i < tileInfo.length; i += 5) {
      const rowTiles = tileInfo.slice(i, i + 5);
      if (rowTiles.length === 5) {
        const word = rowTiles.map((t) => t.extractedLetter).join("");
        rows.push({
          rowIndex: rows.length + 1,
          word: word || "(incomplete)",
          tiles: rowTiles,
        });
      }
    }

    console.log("Grouped into rows:", rows);
    return { tiles: tileInfo, rows };
  };

  // Helper to traverse shadow DOM
  function getShadowRoot(element) {
    if (element && element.shadowRoot) {
      return element.shadowRoot;
    }
    return null;
  }

  // Helper to find game-app in current document
  // Note: If we're running in an iframe (due to all_frames: true),
  // we can directly query the current document
  function findGameApp() {
    // Check if we're in an iframe
    const isInIframe = window.self !== window.top;
    if (DEBUG && isInIframe) {
      console.log("Wordle Solver: Running inside iframe");
    }

    // Try current document (works if we're in the iframe with the game)
    let gameApp = document.querySelector("game-app");
    if (gameApp) {
      if (DEBUG)
        console.log("Wordle Solver: Found game-app in current document");
      return gameApp;
    }

    // Try alternative selectors - Wordle might use different structure
    const alternatives = [
      "wordle-app",
      "wordle-game",
      "[data-wordle]",
      "#wordle",
      ".wordle-game",
      "game-container",
      "[class*='wordle']",
      "[class*='game']",
    ];

    for (const selector of alternatives) {
      const element = document.querySelector(selector);
      if (element) {
        if (DEBUG)
          console.log(
            `Wordle Solver: Found element with selector: ${selector}`
          );
        // Check if it contains game rows
        const rows = element.querySelectorAll("game-row");
        if (rows.length > 0) {
          if (DEBUG)
            console.log(
              `Wordle Solver: Found ${rows.length} game-row elements in ${selector}`
            );
          return element; // Return the container
        }
      }
    }

    // If we're in the main page, try to access iframes (may fail due to CORS)
    if (!isInIframe) {
      const iframes = document.querySelectorAll("iframe");
      if (DEBUG)
        console.log(
          "Wordle Solver: Checking",
          iframes.length,
          "iframes from main page"
        );

      for (const iframe of iframes) {
        try {
          // Log iframe URL to help debug
          const iframeSrc =
            iframe.src || iframe.getAttribute("src") || "no src";
          if (DEBUG) console.log("Wordle Solver: Iframe URL:", iframeSrc);

          // Try to access iframe content (may fail due to CORS)
          const iframeDoc =
            iframe.contentDocument || iframe.contentWindow?.document;
          if (iframeDoc) {
            gameApp = iframeDoc.querySelector("game-app");
            if (gameApp) {
              if (DEBUG)
                console.log(
                  "Wordle Solver: Found game-app in accessible iframe"
                );
              return gameApp;
            }
          }
        } catch (e) {
          // CORS error - can't access iframe (this is expected for cross-origin iframes)
          // The content script should be injected into the iframe itself
          if (DEBUG) {
            const iframeSrc =
              iframe.src || iframe.getAttribute("src") || "no src";
            console.log(
              "Wordle Solver: CORS error accessing iframe:",
              iframeSrc,
              e.message
            );
          }
        }
      }
    }

    return null;
  }

  // Send game state to main page (if we're in an iframe)
  function sendGameStateToMain(state) {
    if (isInIframe && window.parent) {
      try {
        window.parent.postMessage(
          {
            type: MESSAGE_PREFIX + "GAME_STATE",
            state: state,
          },
          "*"
        );
        if (DEBUG)
          console.log("Wordle Solver: Sent game state to main page:", state);
      } catch (e) {
        if (DEBUG) console.error("Wordle Solver: Error sending message:", e);
      }
    }
  }

  // Read Wordle game state - multiple methods for compatibility
  function readGameState() {
    try {
      // Method 0: Try reading from actual Wordle structure (div tiles with data-state)
      // Supports both NYTimes Wordle and Wordle Unlimited
      const tiles = document.querySelectorAll(
        '[data-testid="tile"], [class*="Tile-module"], [role="img"][aria-roledescription="tile"], .tile[data-state]'
      );
      if (tiles.length > 0) {
        if (DEBUG)
          console.log(`Wordle Solver: Found ${tiles.length} tile elements`);

        // Better row grouping: group tiles by their parent container (rows)
        // Strategy: Find all unique parent containers that have exactly 5 tiles
        const parentToTiles = new Map();

        tiles.forEach((tile) => {
          const parent = tile.parentElement;
          if (parent) {
            if (!parentToTiles.has(parent)) {
              parentToTiles.set(parent, []);
            }
            parentToTiles.get(parent).push(tile);
          }
        });

        // Find parents with exactly 5 tiles (likely rows)
        const rowContainers = [];
        const processedTiles = new Set();

        for (const [parent, parentTiles] of parentToTiles.entries()) {
          if (parentTiles.length === 5) {
            // This parent has exactly 5 tiles - likely a row
            const rowTiles = parentTiles.slice(0, 5);
            // Check if any tiles are already processed
            const alreadyProcessed = rowTiles.some((t) =>
              processedTiles.has(t)
            );
            if (!alreadyProcessed) {
              rowTiles.forEach((t) => processedTiles.add(t));
              rowContainers.push(rowTiles);
            }
          }
        }

        // If we didn't find rows by parent, try sequential grouping
        // This works if tiles are in DOM order
        if (rowContainers.length === 0) {
          const tileArray = Array.from(tiles);
          for (let i = 0; i < tileArray.length; i += 5) {
            const rowTiles = tileArray.slice(i, i + 5);
            if (rowTiles.length === 5) {
              rowContainers.push(rowTiles);
            }
          }
        }

        // Sort rows by their position in the DOM (first row = first in DOM)
        // This ensures we read rows in order
        rowContainers.sort((a, b) => {
          const aIndex = Array.from(
            document.querySelectorAll('[data-testid="tile"]')
          ).indexOf(a[0]);
          const bIndex = Array.from(
            document.querySelectorAll('[data-testid="tile"]')
          ).indexOf(b[0]);
          return aIndex - bIndex;
        });

        if (DEBUG) {
          console.log(
            `Wordle Solver: Found ${tiles.length} total tiles, grouped into ${rowContainers.length} rows`
          );
          if (rowContainers.length > 0) {
            console.log(
              "Wordle Solver: Row containers:",
              rowContainers.map((row, idx) => ({
                rowIndex: idx,
                tileCount: row.length,
                firstTileParent: row[0]?.parentElement?.tagName,
                firstTileAriaLabel: row[0]?.getAttribute("aria-label"),
              }))
            );
          }
        }

        const guesses = [];
        const feedback = [];

        rowContainers.forEach((rowTiles, rowIndex) => {
          // First, parse all tiles and extract position info
          const tileData = [];

          rowTiles.forEach((tile) => {
            const ariaLabel = tile.getAttribute("aria-label") || "";
            let letter = "";
            let position = -1;

            // Parse aria-label: "1st letter, R, correct" or "2nd letter, I, absent"
            // Extract position number (1st, 2nd, 3rd, 4th, 5th)
            const positionMatch = ariaLabel.match(
              /(\d+)(?:st|nd|rd|th)\s+letter/i
            );
            if (positionMatch) {
              position = parseInt(positionMatch[1]) - 1; // Convert to 0-based index
            }

            // FIRST: Try to get letter from text content (most reliable - it's directly in the DOM)
            // The tile's textContent contains the letter directly: "p", "r", etc.
            let text = (tile.textContent || "").trim();
            if (!text) {
              text = (tile.innerText || "").trim();
            }

            // Check direct textContent first (most reliable)
            if (text && text.length === 1 && /[a-z]/i.test(text)) {
              letter = text.toLowerCase();
            } else {
              // Also check nested elements
              const possibleSelectors = [
                "span",
                "div",
                "button",
                "[class*='letter']",
                "[class*='tile']",
              ];
              for (const selector of possibleSelectors) {
                const textNode = tile.querySelector(selector);
                if (textNode) {
                  text = (
                    textNode.textContent ||
                    textNode.innerText ||
                    ""
                  ).trim();
                  if (text && text.length === 1 && /[a-z]/i.test(text)) {
                    letter = text.toLowerCase();
                    break;
                  }
                }
              }
            }

            // FALLBACK: Parse letter from aria-label if textContent didn't work
            // Format: "3rd letter, P, absent" - the letter is between commas
            if (!letter || letter.length !== 1 || !/[a-z]/.test(letter)) {
              let match = null;

              // Pattern 1: Match "letter, X, " where X is a single letter (most specific)
              // Example: "3rd letter, P, absent"
              match = ariaLabel.match(/letter,\s*([A-Z])\s*,/i);
              if (match) {
                letter = match[1].toLowerCase();
              } else {
                // Pattern 2: Match ", X, " where X is a single uppercase letter
                match = ariaLabel.match(/,\s*([A-Z])\s*,/i);
                if (match) {
                  letter = match[1].toLowerCase();
                } else {
                  // Pattern 3: Match "letter, X " (with space after X, before next word)
                  match = ariaLabel.match(/letter,\s*([A-Z])\s+/i);
                  if (match) {
                    letter = match[1].toLowerCase();
                  } else {
                    // Pattern 4: Match ", X " (with space after X)
                    match = ariaLabel.match(/,\s*([A-Z])\s+/i);
                    if (match) {
                      letter = match[1].toLowerCase();
                    } else {
                      // Pattern 5: Fallback - find any single uppercase letter
                      match = ariaLabel.match(/\b([A-Z])\b/);
                      if (match) {
                        letter = match[1].toLowerCase();
                      }
                    }
                  }
                }
              }
            }

            // Note: textContent was already checked at the beginning, so this is just a safety check
            // If we still don't have a letter after all attempts, log it for debugging
            if (!letter || letter.length !== 1 || !/[a-z]/.test(letter)) {
              if (DEBUG) {
                console.warn(
                  "Wordle Solver: Could not extract letter from tile:",
                  {
                    ariaLabel,
                    textContent: tile.textContent,
                    innerText: tile.innerText,
                  }
                );
              }
            }

            // Get state from data-state attribute
            const dataState = tile.getAttribute("data-state") || "";

            // If position not found in aria-label, try to infer from DOM order
            if (position === -1) {
              // Use index in rowTiles as fallback
              position = rowTiles.indexOf(tile);
            }

            // Debug logging for first row
            if (DEBUG && rowIndex === 0) {
              console.log("Wordle Solver: Tile parsing:", {
                ariaLabel,
                extractedLetter: letter,
                position,
                dataState,
                textContent: tile.textContent?.trim(),
                innerHTML: tile.innerHTML?.substring(0, 50), // First 50 chars
              });
            }

            // If we still don't have a letter, log a warning
            if (!letter && DEBUG && rowIndex === 0) {
              console.warn(
                "Wordle Solver: Failed to extract letter from tile:",
                {
                  ariaLabel,
                  textContent: tile.textContent,
                  innerText: tile.innerText,
                  allAttributes: Array.from(tile.attributes).map((attr) => ({
                    name: attr.name,
                    value: attr.value,
                  })),
                }
              );
            }

            tileData.push({
              tile,
              letter,
              position,
              dataState: dataState.toLowerCase(),
              ariaLabel,
            });
          });

          // Sort tiles by position to ensure correct order
          tileData.sort((a, b) => a.position - b.position);

          if (DEBUG && rowIndex === 0) {
            console.log(
              "Wordle Solver: Tile data after sorting:",
              tileData.map((t) => ({
                pos: t.position,
                letter: t.letter,
                state: t.dataState,
              }))
            );
          }

          // Now build word and feedback in correct order
          let word = "";
          let rowFeedback = "";
          let hasEvaluation = false;
          let hasLetters = false;
          let allTilesHaveLetters = true;

          tileData.forEach((tileInfo, idx) => {
            const { letter, dataState, position } = tileInfo;

            if (letter && /[a-z]/.test(letter)) {
              word += letter;
              hasLetters = true;

              if (dataState === "correct") {
                rowFeedback += "G";
                hasEvaluation = true;
              } else if (dataState === "present") {
                rowFeedback += "Y";
                hasEvaluation = true;
              } else if (dataState === "absent") {
                rowFeedback += "X";
                hasEvaluation = true;
              } else {
                // Tile has letter but no evaluation yet (might be in transition)
                rowFeedback += "?";
              }

              if (DEBUG && rowIndex === 0) {
                console.log(
                  `Wordle Solver: Position ${position} (idx ${idx}): ${letter} -> ${
                    dataState || "?"
                  }`
                );
              }
            } else {
              allTilesHaveLetters = false;
              if (DEBUG && rowIndex === 0) {
                console.warn(
                  `Wordle Solver: Tile at position ${position} (idx ${idx}) has no valid letter`,
                  {
                    ariaLabel: tileInfo.ariaLabel,
                    textContent: tileInfo.tile.textContent?.trim(),
                  }
                );
              }
            }
          });

          // Validate word - check if all letters are the same (likely a parsing error)
          if (word.length === 5) {
            const uniqueLetters = new Set(word.split(""));
            if (uniqueLetters.size === 1 && DEBUG) {
              console.warn(
                `Wordle Solver: WARNING - Row ${
                  rowIndex + 1
                } has all same letters: ${word}. This might indicate a parsing error.`,
                {
                  tileData: tileData.map((t) => ({
                    letter: t.letter,
                    ariaLabel: t.ariaLabel,
                    dataState: t.dataState,
                  })),
                }
              );
            }
          }

          // Add row if it has a complete word (5 letters)
          // Prefer rows with evaluation, but also include rows that are filled but not yet evaluated
          // This allows us to detect new guesses in real-time
          if (word.length === 5 && hasLetters) {
            // Warn if all letters are the same (likely a parsing error), but still include it
            // This way we can see what's being read and debug the issue
            const uniqueLetters = new Set(word.split(""));
            if (uniqueLetters.size === 1 && DEBUG) {
              console.warn(
                `Wordle Solver: WARNING - Row ${
                  rowIndex + 1
                } has all same letters: ${word}. This might indicate a parsing error.`,
                {
                  tileData: tileData.map((t) => ({
                    letter: t.letter,
                    ariaLabel: t.ariaLabel,
                    dataState: t.dataState,
                    textContent: t.tile.textContent?.trim(),
                  })),
                }
              );
            }
            // Don't skip - include it so we can see what's happening and debug

            if (hasEvaluation) {
              // Row is complete and evaluated - use it
              guesses.push(word);
              feedback.push(rowFeedback);
              if (DEBUG)
                console.log(
                  `Wordle Solver: Row ${
                    rowIndex + 1
                  }: ${word} -> ${rowFeedback}`
                );
            } else if (allTilesHaveLetters) {
              // Row is filled but not yet evaluated - this is likely a new guess
              // We'll include it but mark it as pending
              // Only include if it's the last row (most recent guess)
              if (rowIndex === rowContainers.length - 1) {
                // For pending rows, we'll still try to get suggestions
                // but we'll note that this row might not be fully evaluated yet
                guesses.push(word);
                feedback.push("?????"); // Placeholder feedback
                if (DEBUG)
                  console.log(
                    `Wordle Solver: Row ${
                      rowIndex + 1
                    }: ${word} -> (pending evaluation)`
                  );
              }
            }
          }
        });

        if (guesses.length > 0) {
          if (DEBUG) {
            console.log(
              "Wordle Solver: Found guesses via tile structure:",
              guesses,
              "feedback:",
              feedback,
              "total rows found:",
              rowContainers.length
            );
          }
          const result = { guesses, feedback };
          if (isInIframe) sendGameStateToMain(result);
          return result;
        } else if (rowContainers.length > 0 || tiles.length > 0) {
          // Found rows/tiles but no complete guesses - game detected but no guesses yet
          if (DEBUG) {
            console.log(
              "Wordle Solver: Found",
              rowContainers.length,
              "rows and",
              tiles.length,
              "tiles but no complete guesses yet (new game)"
            );
          }
          // Return empty state so starting words can be shown
          const emptyState = { guesses: [], feedback: [] };
          if (isInIframe) sendGameStateToMain(emptyState);
          return emptyState;
        }
      }

      // Method 0.5: Try to find game-row elements directly (might be in main DOM)
      const directRows = document.querySelectorAll("game-row");
      if (directRows.length > 0) {
        if (DEBUG)
          console.log(
            `Wordle Solver: Found ${directRows.length} game-row elements directly in DOM`
          );
        const guesses = [];
        const feedback = [];

        directRows.forEach((row) => {
          const rowShadow = getShadowRoot(row);
          if (rowShadow) {
            const result = readFromRow(rowShadow);
            if (result) {
              guesses.push(result.word);
              feedback.push(result.feedback);
            }
          } else {
            // Try reading without shadow DOM
            const tiles = row.querySelectorAll("game-tile");
            if (tiles.length === 5) {
              let word = "";
              let rowFeedback = "";
              let hasEvaluation = false;

              tiles.forEach((tile) => {
                const letter =
                  tile.getAttribute("letter") || tile.textContent?.trim() || "";
                const evaluation = tile.getAttribute("evaluation") || "";

                if (letter && letter.length === 1) {
                  word += letter.toLowerCase();
                  if (evaluation === "correct") {
                    rowFeedback += "G";
                    hasEvaluation = true;
                  } else if (evaluation === "present") {
                    rowFeedback += "Y";
                    hasEvaluation = true;
                  } else if (evaluation === "absent") {
                    rowFeedback += "X";
                    hasEvaluation = true;
                  }
                }
              });

              if (word.length === 5 && hasEvaluation) {
                guesses.push(word);
                feedback.push(rowFeedback);
              }
            }
          }
        });

        if (guesses.length > 0) {
          if (DEBUG)
            console.log(
              "Wordle Solver: Found guesses via direct game-row access:",
              guesses
            );
          const result = { guesses, feedback };
          if (isInIframe) sendGameStateToMain(result);
          return result;
        }
      }

      // Method 1: Try nested shadow DOM (official Wordle)
      const gameApp = findGameApp();
      if (DEBUG)
        console.log(
          "Wordle Solver: Checking for game-app...",
          gameApp ? "Found" : "Not found"
        );

      if (gameApp) {
        const shadow1 = getShadowRoot(gameApp);
        if (DEBUG)
          console.log(
            "Wordle Solver: Shadow1:",
            shadow1 ? "Found" : "Not found"
          );

        if (shadow1) {
          const themeManager = shadow1.querySelector("game-theme-manager");
          if (DEBUG)
            console.log(
              "Wordle Solver: Theme manager:",
              themeManager ? "Found" : "Not found"
            );

          if (themeManager) {
            const shadow2 = getShadowRoot(themeManager);
            if (DEBUG)
              console.log(
                "Wordle Solver: Shadow2:",
                shadow2 ? "Found" : "Not found"
              );

            if (shadow2) {
              const game = shadow2.querySelector("#board");
              if (DEBUG)
                console.log(
                  "Wordle Solver: Board:",
                  game ? "Found" : "Not found"
                );

              if (game) {
                const result = readFromBoard(game);
                if (result) {
                  if (DEBUG)
                    console.log(
                      "Wordle Solver: Method 1 result:",
                      result,
                      "guesses:",
                      result.guesses
                    );
                  // Return even if no guesses (empty state is valid)
                  const finalResult = result;
                  if (isInIframe) sendGameStateToMain(finalResult);
                  return finalResult;
                }
              }
            }
          }
        }
      }

      // Method 2: Try direct game-app shadow root
      if (gameApp) {
        const shadow = getShadowRoot(gameApp);
        if (shadow) {
          const board =
            shadow.querySelector("#board") ||
            shadow.querySelector("game-board");
          if (board) {
            const result = readFromBoard(board);
            if (result) {
              if (DEBUG)
                console.log(
                  "Wordle Solver: Method 2 result:",
                  result,
                  "guesses:",
                  result.guesses
                );
              const finalResult = result;
              if (isInIframe) sendGameStateToMain(finalResult);
              return finalResult;
            }
          }
        }
      }

      // Method 3: Try querying all game-row elements (even without shadow DOM access)
      const allRows = document.querySelectorAll("game-row");
      if (DEBUG)
        console.log("Wordle Solver: Found game-row elements:", allRows.length);

      // Method 4: Try to find game-app using more aggressive selectors
      if (!gameApp) {
        // Try waiting a bit and checking again (game might be loading)
        const allGameApps = document.querySelectorAll("game-app");
        if (allGameApps.length > 0) {
          gameApp = allGameApps[0];
          if (DEBUG)
            console.log("Wordle Solver: Found game-app via querySelectorAll");
        }
      }

      if (allRows.length > 0) {
        const guesses = [];
        const feedback = [];

        allRows.forEach((row, index) => {
          if (DEBUG && index === 0) {
            console.log("Wordle Solver: Examining first game-row:", row);
            console.log(
              "Wordle Solver: Row has shadow root:",
              row.shadowRoot ? "yes" : "no"
            );
          }

          const rowShadow = getShadowRoot(row);
          if (rowShadow) {
            const result = readFromRow(rowShadow);
            if (result) {
              guesses.push(result.word);
              feedback.push(result.feedback);
            }
          } else {
            // Try reading without shadow DOM
            const tiles = row.querySelectorAll("game-tile");
            if (DEBUG && index === 0) {
              console.log(
                `Wordle Solver: Row has ${tiles.length} direct game-tile children (no shadow DOM)`
              );
            }

            if (tiles.length === 5) {
              let word = "";
              let rowFeedback = "";
              let hasEvaluation = false;

              tiles.forEach((tile) => {
                const letter =
                  tile.getAttribute("letter") ||
                  tile.textContent?.trim().toLowerCase() ||
                  tile.innerText?.trim().toLowerCase() ||
                  "";
                const evaluation = tile.getAttribute("evaluation") || "";

                if (letter && letter.length === 1 && /[a-z]/.test(letter)) {
                  word += letter;
                  if (evaluation === "correct") {
                    rowFeedback += "G";
                    hasEvaluation = true;
                  } else if (evaluation === "present") {
                    rowFeedback += "Y";
                    hasEvaluation = true;
                  } else if (evaluation === "absent") {
                    rowFeedback += "X";
                    hasEvaluation = true;
                  }
                }
              });

              if (word.length === 5 && hasEvaluation) {
                guesses.push(word);
                feedback.push(rowFeedback);
                if (DEBUG)
                  console.log(
                    `Wordle Solver: Read row ${
                      index + 1
                    } without shadow DOM: ${word} -> ${rowFeedback}`
                  );
              }
            }
          }
        });

        if (guesses.length > 0 || allRows.length > 0) {
          if (DEBUG)
            console.log("Wordle Solver: Method 3 result:", {
              guesses,
              feedback,
              rowsFound: allRows.length,
            });
          const finalResult = { guesses, feedback };
          if (isInIframe) sendGameStateToMain(finalResult);
          return finalResult;
        }
      }

      if (DEBUG) {
        console.log("Wordle Solver: No game state found");
        console.log("Wordle Solver: Running in iframe:", isInIframe);
        console.log("Wordle Solver: Current URL:", window.location.href);

        // Try to provide diagnostic info
        const gameApp = findGameApp();
        if (gameApp) {
          console.log("Wordle Solver: game-app found, checking structure...");
          const shadow1 = getShadowRoot(gameApp);
          if (shadow1) {
            console.log("Wordle Solver: Shadow1 accessible");
            const themeManager = shadow1.querySelector("game-theme-manager");
            console.log(
              "Wordle Solver: Theme manager:",
              themeManager ? "found" : "not found"
            );
            if (themeManager) {
              const shadow2 = getShadowRoot(themeManager);
              console.log(
                "Wordle Solver: Shadow2:",
                shadow2 ? "accessible" : "not accessible"
              );
              if (shadow2) {
                const board = shadow2.querySelector("#board");
                console.log(
                  "Wordle Solver: Board:",
                  board ? "found" : "not found"
                );
              }
            }
          } else {
            console.log("Wordle Solver: Shadow1 not accessible");
          }
        } else {
          console.log("Wordle Solver: game-app element not found");
          // Check if we're on the right page
          const url = window.location.href;
          console.log("Wordle Solver: Current URL:", url);
          if (!url.includes("wordle") && !isInIframe) {
            console.warn("Wordle Solver: Not on a Wordle page! URL:", url);
          }
          // Check for iframes (only if not in iframe ourselves)
          if (!isInIframe) {
            const iframes = document.querySelectorAll("iframe");
            console.log("Wordle Solver: Found iframes:", iframes.length);
            // Log iframe URLs
            iframes.forEach((iframe, index) => {
              const src = iframe.src || iframe.getAttribute("src") || "no src";
              console.log(`Wordle Solver: Iframe ${index + 1} URL:`, src);
            });
          }
        }
      }
      // Return empty state instead of null so we can show starting words
      const emptyState = { guesses: [], feedback: [] };
      if (isInIframe) sendGameStateToMain(emptyState);
      return emptyState;
    } catch (error) {
      console.error("Wordle Solver: Error reading game state:", error);
      return null;
    }
  }

  // Helper to read from board element
  function readFromBoard(board) {
    const rows = board.querySelectorAll("game-row");
    const guesses = [];
    const feedback = [];

    rows.forEach((row) => {
      const rowShadow = getShadowRoot(row);
      if (rowShadow) {
        const result = readFromRow(rowShadow);
        if (result) {
          guesses.push(result.word);
          feedback.push(result.feedback);
        }
      }
    });

    return { guesses, feedback };
  }

  // Helper to read from a row
  function readFromRow(rowShadow) {
    const tiles = rowShadow.querySelectorAll("game-tile");
    if (!tiles || tiles.length === 0) return null;

    let word = "";
    let rowFeedback = "";
    let hasLetters = false;
    let hasEvaluation = false;
    let allTilesHaveLetters = true;

    tiles.forEach((tile, index) => {
      // Try multiple ways to get the letter
      let letter = tile.getAttribute("letter") || "";
      if (!letter) {
        // Try innerText as fallback
        letter = (tile.innerText || tile.textContent || "")
          .trim()
          .toLowerCase();
      }
      // Also try aria-label or data attributes
      if (!letter) {
        const ariaLabel = tile.getAttribute("aria-label") || "";
        const match = ariaLabel.match(/([a-z])/i);
        if (match) letter = match[1].toLowerCase();
      }

      const evaluation = tile.getAttribute("evaluation") || "";

      // Check if tile has a letter (even if not evaluated yet)
      if (letter && letter.length === 1 && /[a-z]/.test(letter)) {
        word += letter.toLowerCase();
        hasLetters = true;

        // Convert evaluation to our format
        if (evaluation === "correct") {
          rowFeedback += "G";
          hasEvaluation = true;
        } else if (evaluation === "present") {
          rowFeedback += "Y";
          hasEvaluation = true;
        } else if (evaluation === "absent") {
          rowFeedback += "X";
          hasEvaluation = true;
        } else {
          // No evaluation yet - check if row is complete
          // If all 5 tiles have letters but no evaluation, it might be submitted but not evaluated yet
          rowFeedback += "?";
        }
      } else {
        allTilesHaveLetters = false;
      }
    });

    // Return row if it has a complete word (5 letters)
    // Accept it even without evaluation if all tiles are filled (might be in transition)
    if (hasLetters && word.length === 5) {
      if (DEBUG) {
        console.log("Wordle Solver: Found row:", {
          word,
          feedback: rowFeedback,
          hasEvaluation,
          length: word.length,
          allTilesHaveLetters,
        });
      }

      // If it has evaluation, definitely return it
      if (hasEvaluation) {
        return { word, feedback: rowFeedback };
      }

      // If all tiles have letters but no evaluation, check if this looks like a submitted row
      // (Wordle sometimes delays showing evaluation)
      // For now, only return rows with evaluation to avoid false positives
      // But log it for debugging
      if (DEBUG && allTilesHaveLetters) {
        console.log(
          "Wordle Solver: Row has letters but no evaluation yet:",
          word
        );
      }
    }
    return null;
  }

  // Get suggestions from API
  async function getSuggestions(guesses, feedback) {
    try {
      // Get ML preference from localStorage (default to false)
      const useML = localStorage.getItem("wordleSolverUseML") === "true";

      if (DEBUG) {
        console.log("Wordle Solver: Calling API with:", {
          guesses,
          feedback,
          useML,
          url: `${API_URL}/suggest`,
        });
      }

      const response = await fetch(`${API_URL}/suggest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          guesses: guesses,
          feedback: feedback,
          use_ml: useML,
        }),
      });

      if (DEBUG) {
        console.log("Wordle Solver: API response status:", response.status);
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error fetching suggestions:", error);
      return { success: false, error: error.message };
    }
  }

  // Get starting words
  async function getStartingWords() {
    try {
      const response = await fetch(`${API_URL}/starting-words`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error fetching starting words:", error);
      return { success: false };
    }
  }

  // Update suggestions display
  async function updateSuggestions() {
    const statusEl = document.getElementById("solver-status");
    const suggestionsDiv = document.getElementById("solver-suggestions");
    const startingWordsDiv = document.getElementById("solver-starting-words");

    if (!statusEl) {
      // Panel not ready yet - try to create it
      if (DEBUG) console.log("Wordle Solver: Panel not ready, creating...");
      createSuggestionsPanel();
      // Wait a bit and try again
      setTimeout(updateSuggestions, 500);
      return;
    }

    const state = readGameState();

    if (!state) {
      // Check if game-app exists
      const gameApp = findGameApp();
      if (!gameApp) {
        if (statusEl) {
          const url = window.location.href;
          if (url.includes("wordle")) {
            statusEl.textContent =
              "Wordle game not detected. Try refreshing the page or check console.";
          } else {
            statusEl.textContent =
              "Not on a Wordle page. Try: NYTimes Wordle or Wordle Unlimited";
          }
        }
        // Show starting words even if game not detected
        if (startingWordsDiv) startingWordsDiv.style.display = "block";
        if (suggestionsDiv) suggestionsDiv.style.display = "none";
        const startingData = await getStartingWords();
        if (startingData.success && startingWordsDiv) {
          const wordsList = document.getElementById("starting-words-list");
          if (wordsList) {
            wordsList.innerHTML = startingData.words
              .slice(0, 5)
              .map(
                (w, i) =>
                  `<div class="starting-word">${i + 1}. ${
                    w.word
                  } (Score: ${Math.round(w.score)})</div>`
              )
              .join("");
          }
        }
      } else {
        if (statusEl) {
          statusEl.textContent =
            "Reading game state... (Check console for debug info)";
        }
        if (DEBUG) {
          console.log("Wordle Solver: Game-app found but state is null");
        }
        // Show starting words while reading
        if (startingWordsDiv) startingWordsDiv.style.display = "block";
        if (suggestionsDiv) suggestionsDiv.style.display = "none";
      }
      return;
    }

    const { guesses, feedback } = state;

    if (DEBUG) {
      console.log("Wordle Solver: Current state:", {
        guesses,
        feedback,
        guessesLength: guesses.length,
      });
    }

    // Filter out rows with pending evaluation (contain "?")
    const evaluatedGuesses = [];
    const evaluatedFeedback = [];
    guesses.forEach((guess, index) => {
      if (feedback[index] && !feedback[index].includes("?")) {
        evaluatedGuesses.push(guess);
        evaluatedFeedback.push(feedback[index]);
      }
    });

    // Check if evaluated state changed
    const stateChanged = !(
      JSON.stringify(evaluatedGuesses) === JSON.stringify(currentGuesses) &&
      JSON.stringify(evaluatedFeedback) === JSON.stringify(currentFeedback)
    );

    // Check if there's a pending row (filled but not yet evaluated)
    const hasPendingRow = guesses.length > evaluatedGuesses.length;

    // Always show starting words if no guesses yet (even if state hasn't changed)
    const shouldShowStartingWords = evaluatedGuesses.length === 0;

    if (!stateChanged && !hasPendingRow && !shouldShowStartingWords) {
      return; // No change at all
    }

    // Update current state if it changed
    if (stateChanged) {
      currentGuesses = evaluatedGuesses;
      currentFeedback = evaluatedFeedback;
    }

    currentGuesses = evaluatedGuesses;
    currentFeedback = evaluatedFeedback;

    if (evaluatedGuesses.length === 0) {
      // New game started - reset game end state
      if (gameEndState) {
        gameEndState = null;
        if (statusEl) {
          statusEl.style.color = "";
          statusEl.style.fontWeight = "";
        }
      }

      // Check if ML mode is enabled
      const useML = localStorage.getItem("wordleSolverUseML") === "true";

      if (useML) {
        // Use ML model suggestions even with no guesses
        const startingWordsDiv = document.getElementById(
          "solver-starting-words"
        );
        const suggestionsDiv = document.getElementById("solver-suggestions");

        if (startingWordsDiv) startingWordsDiv.style.display = "none";
        if (suggestionsDiv) suggestionsDiv.style.display = "block";

        if (statusEl) {
          statusEl.textContent = "Turn 1/6 (ML) - Getting suggestions...";
        }

        const result = await getSuggestions([], []);
        if (result.success && result.suggestions) {
          const suggestionsList = document.getElementById("solver-suggestions");
          if (suggestionsList) {
            suggestionsList.innerHTML = result.suggestions
              .slice(0, 10)
              .map(
                (word, i) =>
                  `<div class="suggestion-word">${
                    i + 1
                  }. ${word.toUpperCase()}</div>`
              )
              .join("");
          }
          if (statusEl) {
            statusEl.textContent = `Turn 1/6 (ML) - ${result.suggestions.length} suggestions`;
          }
        } else {
          if (statusEl) {
            statusEl.textContent = "Error getting ML suggestions";
          }
        }
      } else {
        // Show starting words from LetterAnalyzer (baseline)
        const startingWordsDiv = document.getElementById(
          "solver-starting-words"
        );
        const suggestionsDiv = document.getElementById("solver-suggestions");

        if (startingWordsDiv) startingWordsDiv.style.display = "block";
        if (suggestionsDiv) suggestionsDiv.style.display = "none";

        const startingData = await getStartingWords();
        if (startingData.success) {
          const wordsList = document.getElementById("starting-words-list");
          if (wordsList) {
            wordsList.innerHTML = startingData.words
              .slice(0, 5)
              .map(
                (w, i) =>
                  `<div class="starting-word">${i + 1}. ${
                    w.word
                  } (Score: ${Math.round(w.score)})</div>`
              )
              .join("");
          }
          if (statusEl) {
            statusEl.textContent = "No guesses yet - Best starting words:";
          }
        } else {
          if (statusEl) {
            statusEl.textContent = "Error loading starting words";
          }
        }
      }
    } else {
      // Show suggestions
      const startingWordsDiv = document.getElementById("solver-starting-words");
      const suggestionsDiv = document.getElementById("solver-suggestions");

      if (startingWordsDiv) startingWordsDiv.style.display = "none";
      if (suggestionsDiv) suggestionsDiv.style.display = "block";

      // Check if there's a pending row (not yet evaluated)
      const hasPendingRow = guesses.length > evaluatedGuesses.length;
      const turnNumber = hasPendingRow
        ? evaluatedGuesses.length + 1
        : evaluatedGuesses.length + 1;

      // Don't update status if game has ended (solved or failed)
      if (statusEl && !gameEndState) {
        const useML = localStorage.getItem("wordleSolverUseML") === "true";
        const solverType = useML ? "ML" : "Baseline";
        if (hasPendingRow) {
          statusEl.textContent = `Turn ${turnNumber}/6 (${solverType}) - Waiting for evaluation...`;
        } else {
          statusEl.textContent = `Turn ${turnNumber}/6 (${solverType}) - Getting suggestions...`;
        }
      }

      if (DEBUG) {
        const useML = localStorage.getItem("wordleSolverUseML") === "true";
        console.log("Wordle Solver: Requesting suggestions for:", {
          guesses: evaluatedGuesses,
          feedback: evaluatedFeedback,
          hasPendingRow,
          allGuesses: guesses, // Include pending guesses for debugging
          solver: useML ? "ML" : "Baseline",
        });
        console.log(
          "Wordle Solver: Already guessed words that should be filtered:",
          evaluatedGuesses
        );
      }

      // Check if guesses look suspicious (all same letters)
      const suspiciousGuesses = evaluatedGuesses.filter((guess) => {
        if (guess.length !== 5) return false;
        const uniqueLetters = new Set(guess.split(""));
        return uniqueLetters.size === 1;
      });

      if (suspiciousGuesses.length > 0 && DEBUG) {
        console.warn(
          "Wordle Solver: Detected suspicious guesses (all same letters):",
          suspiciousGuesses
        );
        if (statusEl) {
          statusEl.textContent = `Turn ${turnNumber}/6 - Warning: Some guesses may be misread. Check console.`;
        }
      }

      const result = await getSuggestions(evaluatedGuesses, evaluatedFeedback);

      if (result.success) {
        if (suggestionsDiv) {
          suggestionsDiv.innerHTML = `
                    <div class="suggestions-header">Top Suggestions:</div>
                    ${result.suggestions
                      .map(
                        (word, i) =>
                          `<div class="suggestion ${
                            i === 0 ? "top-suggestion" : ""
                          }">${i + 1}. ${word.toUpperCase()}</div>`
                      )
                      .join("")}
                    <div class="candidates-count">${
                      result.num_candidates
                    } valid candidates remaining</div>
                `;
        }
        // Don't update status if game has ended (solved or failed)
        if (statusEl && !gameEndState) {
          statusEl.textContent = `Turn ${turnNumber}/6`;
        }
        if (DEBUG) {
          console.log(
            "Wordle Solver: Suggestions received:",
            result.suggestions
          );
        }
      } else {
        if (statusEl) {
          statusEl.textContent = `Error: ${
            result.error || "Failed to get suggestions"
          }`;
        }
        if (suggestionsDiv) {
          suggestionsDiv.innerHTML =
            '<div class="error">Make sure the Python server is running!</div>';
        }
        if (DEBUG) {
          console.error(
            "Wordle Solver: Failed to get suggestions:",
            result.error
          );
        }
      }
    }
  }

  // Track game state to avoid duplicate notifications
  let gameEndState = null; // 'solved', 'failed', or null

  // Check if word is solved or failed
  function checkIfSolved() {
    const state = readGameState();
    if (!state || state.feedback.length === 0) return;

    const evaluatedGuesses = [];
    const evaluatedFeedback = [];
    state.guesses.forEach((guess, index) => {
      if (state.feedback[index] && !state.feedback[index].includes("?")) {
        evaluatedGuesses.push(guess);
        evaluatedFeedback.push(state.feedback[index]);
      }
    });

    if (evaluatedGuesses.length === 0) return;

    const lastFeedback = evaluatedFeedback[evaluatedFeedback.length - 1];
    const numGuesses = evaluatedGuesses.length;

    // Check if solved (all greens)
    if (lastFeedback === "GGGGG") {
      if (gameEndState !== "solved") {
        gameEndState = "solved";
        const solvedWord = evaluatedGuesses[evaluatedGuesses.length - 1];

        // Track the solved word
        fetch(`${API_URL}/track-solved`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ word: solvedWord }),
        }).catch((err) => console.error("Error tracking word:", err));

        // Update panel to show solved message
        const statusEl = document.getElementById("solver-status");
        if (statusEl) {
          statusEl.textContent = `🎉 Solved in ${numGuesses}/6! Word: ${solvedWord.toUpperCase()}`;
          statusEl.style.color = "#4CAF50";
          statusEl.style.fontWeight = "bold";
        }

        if (DEBUG) {
          console.log(
            `Wordle Solver: Game solved in ${numGuesses} guesses! Word: ${solvedWord}`
          );
        }
      }
      return;
    }

    // Check if failed (6 guesses without solving)
    if (numGuesses >= 6 && lastFeedback !== "GGGGG") {
      if (gameEndState !== "failed") {
        gameEndState = "failed";

        // Update panel to show failed message
        const statusEl = document.getElementById("solver-status");
        if (statusEl) {
          statusEl.textContent = `❌ Failed after 6 guesses`;
          statusEl.style.color = "#f44336";
          statusEl.style.fontWeight = "bold";
        }

        if (DEBUG) {
          console.log("Wordle Solver: Game failed after 6 guesses");
        }
      }
      return;
    }

    // Game still in progress - reset end state if needed
    if (gameEndState && numGuesses < 6 && lastFeedback !== "GGGGG") {
      gameEndState = null;
      const statusEl = document.getElementById("solver-status");
      if (statusEl) {
        statusEl.style.color = "";
        statusEl.style.fontWeight = "";
      }
    }
  }

  // Watch for changes to game tiles
  let tileObserver = null;
  function watchForTileChanges() {
    if (tileObserver) {
      tileObserver.disconnect();
    }

    // Watch for changes to tiles
    tileObserver = new MutationObserver((mutations) => {
      let shouldUpdate = false;

      mutations.forEach((mutation) => {
        // Check if tiles were added or modified
        if (mutation.type === "childList") {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) {
              // Element node
              if (
                node.hasAttribute &&
                (node.hasAttribute("data-testid") ||
                  node.classList?.contains("tile") ||
                  node.querySelector('[data-testid="tile"]') ||
                  node.querySelector(".tile[data-state]"))
              ) {
                shouldUpdate = true;
              }
            }
          });
        } else if (mutation.type === "attributes") {
          // Check if data-state or aria-label changed (evaluation updates)
          // Also check if class changed (for .tile elements)
          if (
            mutation.target.hasAttribute("data-state") ||
            mutation.target.hasAttribute("aria-label") ||
            mutation.target.hasAttribute("data-testid") ||
            (mutation.attributeName === "class" &&
              mutation.target.classList?.contains("tile"))
          ) {
            shouldUpdate = true;
          }
        }
      });

      if (shouldUpdate) {
        if (DEBUG)
          console.log("Wordle Solver: Tile changes detected, updating...");
        setTimeout(() => {
          updateSuggestions();
          checkIfSolved();
        }, 300); // Small delay to let DOM settle
      }
    });

    // Observe the document body for tile changes
    const observeTarget = document.body || document.documentElement;
    if (observeTarget) {
      tileObserver.observe(observeTarget, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ["data-state", "aria-label", "data-testid", "class"],
      });
      if (DEBUG)
        console.log("Wordle Solver: Started watching for tile changes");
    }
  }

  // Initialize - always create panel first
  function init() {
    try {
      if (DEBUG) console.log("Wordle Solver: Initializing...");
      createSuggestionsPanel();

      if (DEBUG) console.log("Wordle Solver: Panel created");

      // Start watching for tile changes
      watchForTileChanges();

      // Start updating immediately
      updateSuggestions();

      // Update every 1 second for more responsive updates
      const updateInterval = setInterval(() => {
        updateSuggestions();
        checkIfSolved();
      }, 1000);

      // Also update on keyboard events
      document.addEventListener("keydown", () => {
        setTimeout(updateSuggestions, 300);
      });

      // Update on mouse clicks (for clicking tiles)
      document.addEventListener("click", () => {
        setTimeout(updateSuggestions, 300);
      });

      // Update when input changes (typing)
      document.addEventListener("input", () => {
        setTimeout(updateSuggestions, 300);
      });

      if (DEBUG) console.log("Wordle Solver: Initialization complete");
    } catch (error) {
      console.error("Wordle Solver: Error during initialization:", error);
    }
  }

  // Wait for page to load - but always show panel
  let checkCount = 0;
  const MAX_CHECKS = 60; // 30 seconds max wait (game loads slowly)
  let gameFound = false;

  function waitForWordle() {
    try {
      const gameApp = findGameApp();
      if (gameApp) {
        if (!gameFound) {
          gameFound = true;
          if (DEBUG) console.log("Wordle Solver: Game found, initializing...");
          init();
        }
      } else {
        checkCount++;
        if (checkCount < MAX_CHECKS) {
          // Keep checking until game-app appears
          // Check more frequently at first, then slow down
          const delay = checkCount < 10 ? 200 : 500;
          setTimeout(waitForWordle, delay);
        } else {
          // Timeout - still initialize to show panel
          if (DEBUG)
            console.warn(
              "Wordle Solver: Game-app not found after " +
                MAX_CHECKS * 0.5 +
                " seconds, but initializing anyway"
            );
          // Try one more time with a longer wait
          setTimeout(() => {
            const finalCheck = findGameApp();
            if (finalCheck && !gameFound) {
              gameFound = true;
              if (DEBUG)
                console.log("Wordle Solver: Found game-app on final check!");
              init();
            } else if (!gameFound) {
              init(); // Initialize anyway
            }
          }, 2000);
        }
      }
    } catch (error) {
      console.error("Wordle Solver: Error in waitForWordle:", error);
      // Still try to initialize
      if (!gameFound) {
        init();
      }
    }
  }

  // Also watch for game-app being added to DOM
  function watchForGameApp() {
    if (gameFound) return;

    const observer = new MutationObserver((mutations) => {
      const gameApp = findGameApp();
      if (gameApp && !gameFound) {
        gameFound = true;
        if (DEBUG)
          console.log("Wordle Solver: Game-app detected via MutationObserver!");
        observer.disconnect();
        init();
      }
    });

    observer.observe(document.body || document.documentElement, {
      childList: true,
      subtree: true,
    });

    // Stop observing after 30 seconds
    setTimeout(() => {
      observer.disconnect();
    }, 30000);
  }

  // Listen for messages from iframes (if we're on main page)
  if (!isInIframe) {
    window.addEventListener("message", (event) => {
      // Accept messages from any origin (since iframe might be cross-origin)
      if (
        event.data &&
        event.data.type &&
        event.data.type.startsWith(MESSAGE_PREFIX)
      ) {
        if (DEBUG)
          console.log(
            "Wordle Solver: Received message from iframe:",
            event.data
          );

        if (event.data.type === MESSAGE_PREFIX + "GAME_STATE") {
          // Update suggestions with state from iframe
          const state = event.data.state;
          if (state) {
            currentGuesses = state.guesses || [];
            currentFeedback = state.feedback || [];
            updateSuggestions();
          }
        }
      }
    });
  }

  // Start immediately - don't wait for DOMContentLoaded
  let extensionStarted = false;

  function startExtension() {
    if (extensionStarted) {
      if (DEBUG) console.log("Wordle Solver: Already started, skipping...");
      return;
    }
    extensionStarted = true;

    try {
      if (DEBUG) {
        console.log("Wordle Solver: Script loaded, starting...");
        console.log("Wordle Solver: Running in iframe:", isInIframe);
        console.log("Wordle Solver: Current URL:", window.location.href);
        // Run diagnosis after a delay
        setTimeout(() => {
          diagnoseWordleStructure();
        }, 5000); // Wait 5 seconds for game to fully load
      }

      // Try to create panel immediately
      if (document.body) {
        createSuggestionsPanel();
      } else {
        // Wait for body
        const bodyObserver = new MutationObserver(() => {
          if (document.body && !suggestionsPanel) {
            bodyObserver.disconnect();
            createSuggestionsPanel();
          }
        });
        bodyObserver.observe(document.documentElement, {
          childList: true,
          subtree: true,
        });

        // Also try after a short delay
        setTimeout(() => {
          if (document.body && !suggestionsPanel) {
            createSuggestionsPanel();
          }
        }, 100);
      }

      // Wait for Wordle game
      waitForWordle();

      // Also watch for game-app being added dynamically
      if (document.body) {
        watchForGameApp();
      } else {
        // Wait for body, then watch
        const bodyObserver = new MutationObserver(() => {
          if (document.body) {
            bodyObserver.disconnect();
            watchForGameApp();
          }
        });
        bodyObserver.observe(document.documentElement, {
          childList: true,
        });
      }

      // Verify panel was created after a delay
      setTimeout(() => {
        const panel = document.getElementById("wordle-solver-panel");
        if (!panel) {
          console.error(
            "Wordle Solver: Panel was not created! Trying again..."
          );
          suggestionsPanel = null; // Reset
          createSuggestionsPanel();
        } else if (DEBUG) {
          console.log("Wordle Solver: Panel verified in DOM");
        }
      }, 1000);
    } catch (error) {
      console.error("Wordle Solver: Fatal error:", error);
      // Try to show error in page
      try {
        const errorDiv = document.createElement("div");
        errorDiv.style.cssText =
          "position:fixed;top:20px;right:20px;background:red;color:white;padding:20px;z-index:99999;";
        errorDiv.textContent = "Wordle Solver Error: " + error.message;
        if (document.body) {
          document.body.appendChild(errorDiv);
        }
      } catch (e) {
        // Can't even show error
      }
    }
  }

  // Run when script loads
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startExtension);
  } else {
    // DOM already loaded
    startExtension();
  }

  // Also try immediately (in case DOMContentLoaded already fired)
  setTimeout(() => {
    if (!extensionStarted && document.body) {
      startExtension();
    }
  }, 50);
})();
