<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brevet Times API Consumer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 30px;
        }

        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .controls {
            display: grid;
            gap: 20px;
            margin-bottom: 30px;
        }

        .button-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            justify-content: center;
        }

        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .options-group {
            display: flex;
            gap: 20px;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
        }

        .option {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        label {
            font-weight: 600;
            color: #555;
            font-size: 14px;
        }

        select, input[type="number"] {
            padding: 10px 15px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            min-width: 150px;
        }

        #results {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            min-height: 200px;
            margin-top: 20px;
        }

        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        tr:hover {
            background: #f5f5f5;
        }

        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }

        .error {
            background: #fee;
            border: 2px solid #fcc;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚴 Brevet Times API Consumer</h1>
        
        <div class="info-box">
            <p><strong>Instructions:</strong></p>
            <p>1. Select your preferred output format (JSON or CSV)</p>
            <p>2. Optionally enter a number for "Top K Results"</p>
            <p>3. Click one of the buttons below to fetch data</p>
        </div>

        <form method="GET" action="">
            <div class="controls">
                <div class="button-group">
                    <button type="submit" name="action" value="listAll">📋 List All Times</button>
                    <button type="submit" name="action" value="listOpenOnly">🟢 List Open Only</button>
                    <button type="submit" name="action" value="listCloseOnly">🔴 List Close Only</button>
                </div>
                
                <div class="options-group">
                    <div class="option">
                        <label for="format">Output Format:</label>
                        <select name="format" id="format">
                            <option value="json" <?php echo (isset($_GET['format']) && $_GET['format'] == 'json') ? 'selected' : ''; ?>>JSON</option>
                            <option value="csv" <?php echo (isset($_GET['format']) && $_GET['format'] == 'csv') ? 'selected' : ''; ?>>CSV</option>
                        </select>
                    </div>
                    
                    <div class="option">
                        <label for="top">Top K Results (optional):</label>
                        <input type="number" name="top" id="top" min="1" max="50" 
                               value="<?php echo isset($_GET['top']) ? htmlspecialchars($_GET['top']) : ''; ?>" 
                               placeholder="Leave empty for all">
                    </div>
                </div>
            </div>
        </form>

        <div id="results">
            <?php
            if (isset($_GET['action'])) {
                $action = $_GET['action'];
                $format = isset($_GET['format']) ? $_GET['format'] : 'json';
                $top = isset($_GET['top']) && !empty($_GET['top']) ? $_GET['top'] : '';
                
                // Build API URL
                $api_base = 'http://laptop:5000';
                $url = "$api_base/$action/$format";
                
                if (!empty($top)) {
                    $url .= "?top=$top";
                }
                
                // Fetch data from API
                $ch = curl_init();
                curl_setopt($ch, CURLOPT_URL, $url);
                curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($ch, CURLOPT_TIMEOUT, 10);
                
                $response = curl_exec($ch);
                $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
                $error = curl_error($ch);
                curl_close($ch);
                
                if ($error) {
                    echo "<div class='error'><strong>Error:</strong> Failed to connect to API: $error</div>";
                } elseif ($http_code != 200) {
                    echo "<div class='error'><strong>Error:</strong> API returned status code $http_code</div>";
                } else {
                    echo "<h3>" . strtoupper($format) . " Response:</h3>";
                    
                    if ($format == 'json') {
                        $data = json_decode($response, true);
                        if ($data === null) {
                            echo "<div class='error'>Failed to parse JSON response</div>";
                        } else {
                            echo "<pre>" . json_encode($data, JSON_PRETTY_PRINT) . "</pre>";
                        }
                    } else {
                        // CSV format - display as table
                        $lines = explode("\n", trim($response));
                        if (count($lines) > 0) {
                            echo "<table>";
                            
                            // Header row
                            $headers = str_getcsv($lines[0]);
                            echo "<thead><tr>";
                            foreach ($headers as $header) {
                                echo "<th>" . htmlspecialchars($header) . "</th>";
                            }
                            echo "</tr></thead>";
                            
                            // Data rows
                            echo "<tbody>";
                            for ($i = 1; $i < count($lines); $i++) {
                                if (empty($lines[$i])) continue;
                                $cells = str_getcsv($lines[$i]);
                                echo "<tr>";
                                foreach ($cells as $cell) {
                                    echo "<td>" . htmlspecialchars($cell) . "</td>";
                                }
                                echo "</tr>";
                            }
                            echo "</tbody>";
                            echo "</table>";
                        }
                    }
                }
            } else {
                echo "<p style='text-align: center; color: #999; font-style: italic; padding: 40px;'>Results will appear here...</p>";
            }
            ?>
        </div>
    </div>
</body>
</html>